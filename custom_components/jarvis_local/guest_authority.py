"""Persisted guest authority ownership; no speaker identity or automation cancellation."""
import asyncio
from datetime import timedelta
import logging
from time import monotonic
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)
KEY = 'jarvis_local.guest_authority'
AUTO_KEYS = ('guest_mode', 'visitors_present', 'guests_staying', 'guest_auto_enable',
             'guest_owner_one', 'guest_owner_two', 'guest_away_suspend')


class GuestAuthority:
    def __init__(self, hass, store, context, clock=monotonic):
        self.hass, self.store, self.context, self.clock = hass, store, context, clock
        self.record = {}
        self.since = None
        self.epoch = 0
        self.override = None
        self.lock = asyncio.Lock()
        self.unsubs = []
        self.stopped = False
        self.error = None
        self.restart_cleanup = False

    def settings(self):
        return self.hass.data['jarvis_local'].get('settings', {})

    def state(self, entity):
        value = self.hass.states.get(entity) if entity else None
        return value.state if value else None

    def value(self, key):
        return self.state(self.settings().get(key))

    async def persist(self):
        await self.store.async_save(dict(self.record))

    async def write(self, entity, value):
        if not isinstance(entity, str) or not entity.startswith('input_boolean.'):
            raise ValueError('Invalid guest helper entity')
        if self.state(entity) not in {'on', 'off'}:
            raise ValueError('A configured guest helper is unavailable')
        if self.state(entity) != value:
            await self.hass.services.async_call('input_boolean', 'turn_' + value,
                {'entity_id': entity}, blocking=True, context=self.context)
            if self.state(entity) != value:
                raise ValueError('A guest helper did not confirm its requested state')

    async def start(self):
        from homeassistant.helpers.event import async_track_time_interval
        saved = await self.store.async_load()
        if isinstance(saved, dict) and saved.get('authority') in {'none', 'manual', 'automatic'}:
            self.record = saved
        # Never use a persisted elapsed timer. Reconcile old automatic authority
        # before starting a fresh continuous-away observation.
        self.restart_cleanup = self.record.get('authority') == 'automatic'
        self.unsubs = [self.hass.bus.async_listen('state_changed', self.changed),
                       async_track_time_interval(self.hass, self.tick, timedelta(seconds=5))]
        await self.tick()

    async def stop(self):
        self.stopped = True
        for unsubscribe in self.unsubs:
            unsubscribe()
        self.unsubs = []
        async with self.lock:
            self.since = None
            try:
                await self.revoke()
            except (HomeAssistantError, ValueError, OSError, TimeoutError) as err:
                _LOGGER.warning('Could not release automatic guest authority during unload: %s', type(err).__name__)
        # Never clear manual handovers on unload.

    @callback
    def changed(self, event):
        settings = self.settings()
        entity = event.data.get('entity_id')
        if entity not in set(settings.get(key) for key in (*AUTO_KEYS, 'guest_names', 'guest_staying_names')):
            return
        old = event.data.get('old_state')
        new = event.data.get('new_state')
        before = old.state if old else None
        after = new.state if new else None
        if before == after:
            return
        own = getattr(getattr(event, 'context', None), 'id', None) == self.context.id
        if not own:
            self.epoch += 1
            self.since = None
            if entity == settings.get('guest_mode') and before in {'on', 'off'} and after in {'on', 'off'}:
                self.override = after
        if not self.stopped:
            self.hass.async_create_task(self.tick())

    async def apply_override(self):
        if self.override is None:
            return
        state, self.override = self.override, None
        self.record.update(authority='manual' if state == 'on' else 'none',
                           mode_entity=self.settings().get('guest_mode'), blocked=state == 'off')
        await self.persist()

    def eligible(self):
        settings = self.settings()
        boolean_keys=('guest_mode', 'visitors_present', 'guests_staying', 'guest_auto_enable', 'guest_away_suspend')
        if len({settings.get(key) for key in boolean_keys}) != len(boolean_keys):
            return False
        if settings.get('guest_owner_one') == settings.get('guest_owner_two'):
            return False
        return (all(settings.get(key) for key in AUTO_KEYS)
                and self.value('guest_auto_enable') == 'on'
                and self.value('visitors_present') == 'on'
                and self.value('guests_staying') == 'on'
                and self.value('guest_owner_one') == self.value('guest_owner_two') == 'not_home'
                and self.value('guest_mode') in {'on', 'off'}
                and self.value('guest_away_suspend') in {'on', 'off'}
                and self.names_available())

    def names_available(self):
        settings = self.settings()
        if not settings.get('guest_staying_names') or not settings.get('guest_names'):
            return False
        source = self.hass.states.get(settings.get('guest_staying_names'))
        target = self.hass.states.get(settings.get('guest_names'))
        return bool(source and target and source.state not in {'', 'unknown', 'unavailable'}
                    and target.state not in {'unknown', 'unavailable'}
                    and len(source.state) <= target.attributes.get('max', 255))

    async def prepare_settings(self, new):
        async with self.lock:
            if any(self.settings().get(key) != new.get(key) for key in (*AUTO_KEYS, 'guest_names', 'guest_staying_names')):
                self.epoch += 1
                await self.apply_override()
                await self.revoke()
                await self.release_suspension()
                self.record = {'authority':'none', 'mode_entity':new.get('guest_mode')}
                await self.persist()

    async def release_suspension(self):
        if self.record.get('suspend_owned'):
            await self.write(self.record.get('suspend_entity'), 'off')
            self.record['suspend_owned'] = False
            await self.persist()

    async def revoke(self):
        # Only the recorded automatic helper may be revoked. A configuration
        # change cannot redirect this write to a different manual helper.
        if self.record.get('authority') == 'automatic':
            await self.write(self.record.get('mode_entity'), 'off')
            self.record['authority'] = 'none'
            await self.persist()
        if self.record.get('authority') != 'manual':
            await self.release_suspension()
        self.since = None

    async def pending_valid(self, epoch):
        # Treat a newly on helper as manual even if its state_changed callback
        # has not been dispatched yet. Pending automatic work cannot claim it.
        if self.value('guest_mode') == 'on':
            self.override = 'on'
        if self.override is not None:
            await self.apply_override()
            return False
        if epoch != self.epoch or not self.eligible():
            await self.revoke()
            return False
        return True

    async def tick(self, now=None):
        if self.stopped:
            return
        async with self.lock:
            if self.stopped:
                return
            try:
                await self.apply_override()
                if self.restart_cleanup:
                    await self.revoke()
                    self.restart_cleanup = False
                settings = self.settings()
                if self.record.get('mode_entity') != settings.get('guest_mode'):
                    await self.revoke()
                    self.record = {'authority': 'none', 'mode_entity': settings.get('guest_mode')}
                    await self.persist()
                if self.record.get('authority') not in {'automatic', 'manual'} and self.value('guest_mode') == 'on':
                    self.record['authority'] = 'manual'
                    await self.persist()
                if self.record.get('authority') == 'manual':
                    self.since = None
                    if self.value('guest_mode') == 'off':
                        self.record.update(authority='none', blocked=True)
                        await self.persist()
                        await self.release_suspension()
                    return
                if self.record.get('authority') == 'automatic':
                    if not self.record.get('active') or not self.eligible():
                        await self.revoke()
                    return
                if self.value('guest_mode') == 'off':
                    await self.release_suspension()
                if self.value('guests_staying') == 'off' or 'home' in (
                        self.value('guest_owner_one'), self.value('guest_owner_two')):
                    if self.record.get('blocked'):
                        self.record['blocked'] = False
                        await self.persist()
                if not self.eligible() or self.record.get('blocked'):
                    self.since = None
                    return
                if self.since is None:
                    self.since = self.clock()
                if self.clock() - self.since < 120:
                    return
                epoch = self.epoch
                self.record.update(authority='automatic', mode_entity=settings['guest_mode'],
                    active=False,
                    suspend_entity=settings['guest_away_suspend'],
                    suspend_owned=self.value('guest_away_suspend') == 'off')
                # Write ownership before side effects; recovery can safely
                # remove any automatic writes after interruption.
                await self.persist()
                if not await self.pending_valid(epoch):
                    return
                await self.write(settings['guest_away_suspend'], 'on')
                if not await self.pending_valid(epoch):
                    return
                await self.hass.services.async_call('input_text', 'set_value',
                    {'entity_id':settings['guest_names'], 'value':self.value('guest_staying_names')},
                    blocking=True, context=self.context)
                if not await self.pending_valid(epoch):
                    return
                await self.write(settings['guest_mode'], 'on')
                self.record['active'] = True
                await self.persist()
                self.error = None
            except (HomeAssistantError, ValueError, OSError, TimeoutError) as err:
                self.since = None
                self.error = type(err).__name__
                _LOGGER.warning('Guest authority reconciliation failed: %s', self.error)

    async def command(self, data, context=None):
        async with self.lock:
            if self.stopped:
                raise ValueError('Guest handover controller is not active')
            await self.apply_override()
            operation = data['operation']
            settings = self.settings()
            if operation == 'status':
                return ('Guest Mode is ' + str(self.value('guest_mode')) + '. Authority: '
                        + self.record.get('authority', 'none') + '.'
                        + (' In charge: ' + str(self.value('guest_names')) + '.' if self.value('guest_mode') == 'on' else ''))
            self.epoch += 1
            self.since = None
            if operation == 'set':
                self.record.update(authority='manual', mode_entity=settings['guest_mode'], blocked=False)
                await self.persist()
                await self.hass.services.async_call('input_text', 'set_value',
                    {'entity_id':settings['guest_names'], 'value':data['names']}, blocking=True, context=context)
                await self.write(settings['guest_mode'], 'on')
                return 'Guest Mode is on. In charge: ' + data['names'] + '.'
            if operation == 'cancel':
                self.record.update(authority='none', mode_entity=settings['guest_mode'], blocked=True)
                await self.persist()
                await self.write(settings['guest_mode'], 'off')
                await self.release_suspension()
                await self.hass.services.async_call('input_text', 'set_value',
                    {'entity_id':settings['guest_names'], 'value':''}, blocking=True, context=context)
                return 'Guest handover cancelled. Automatic handover is paused until an owner returns or staying is declared again.'
            if operation == 'staying':
                await self.hass.services.async_call('input_text', 'set_value',
                    {'entity_id':settings['guest_staying_names'], 'value':data['names']}, blocking=True, context=context)
                await self.write(settings['visitors_present'], 'on')
                await self.write(settings['guests_staying'], 'on')
                self.record['blocked'] = False
                await self.persist()
                return 'Guests recorded as staying. Visitor speech is active. No new authority has been granted.'
            if operation == 'clear':
                await self.write(settings['guests_staying'], 'off')
                await self.write(settings['visitors_present'], 'off')
                await self.revoke()
                await self.hass.services.async_call('input_text', 'set_value',
                    {'entity_id':settings['guest_staying_names'], 'value':''}, blocking=True, context=context)
                if self.record.get('authority') == 'manual':
                    return 'Visitors and staying cleared. The manual guest handover remains in place; cancel it explicitly if needed.'
                await self.hass.services.async_call('input_text', 'set_value',
                    {'entity_id':settings['guest_names'], 'value':''}, blocking=True, context=context)
                return 'Visitors and staying cleared. Automatic guest authority is off.'
            raise ValueError('Unsupported guest operation')


async def create(hass):
    from homeassistant.core import Context
    from homeassistant.helpers.storage import Store
    manager = GuestAuthority(hass, Store(hass, 1, KEY), Context())
    await manager.start()
    return manager
