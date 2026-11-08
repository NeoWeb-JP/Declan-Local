"""Review static catalogue text before explicitly requesting any paid synthesis."""
import asyncio
from hashlib import sha256
import json
from pathlib import Path
import secrets
from time import monotonic

from .voice_catalog_fallback import load_catalogue
from .voice_text import spoken_text
STATIC_CATEGORIES = frozenset({'general','on','off','brightness','morning','self_correction',
                               'bedtime','movie','welcome_edd','changed_mind','clarification','repeat'})


class CataloguePreparation:
    def __init__(self, manager, clock=monotonic):
        self.manager = manager
        self.clock = clock
        self.reviews = {}
        self.lock = asyncio.Lock()

    async def lines(self, modes):
        if not isinstance(modes,list) or not modes or any(not isinstance(m,str) or m not in {'Home','Guest'} for m in modes) or len(modes)!=len(set(modes)):
            raise ValueError('Choose Home, Guest or both')
        catalogue = await self.manager.hass.async_add_executor_job(
            load_catalogue, Path(__file__).with_name('responses.json'))
        lines = []
        for mode in modes:
            pools = catalogue.get(mode)
            if not isinstance(pools,dict):
                raise ValueError('Catalogue is unavailable')
            for category, values in pools.items():
                if category not in STATIC_CATEGORIES or not isinstance(values,list):
                    raise ValueError('Invalid catalogue')
                for sentence in values:
                    if not isinstance(sentence,str) or not sentence.strip() or len(sentence)>(300 if category == 'welcome_edd' else 200) or any(c in sentence for c in '{}'):
                        raise ValueError('Catalogue must contain short static sentences only')
                    key = sha256(json.dumps([mode,category,sentence],ensure_ascii=False).encode()).hexdigest()
                    if not any(line['id']==key for line in lines):
                        lines.append({'id':key,'mode':mode,'category':category,'text':sentence,
                                      'spoken_text':spoken_text(sentence),'characters':len(spoken_text(sentence))})
        if not lines or len(lines)>250 or sum(line['characters'] for line in lines)>50000:
            raise ValueError('Catalogue size is outside preparation limits')
        digest = sha256(json.dumps(lines,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        return lines, digest

    async def plan(self, modes):
        lines, digest = await self.lines(modes)
        manager = self.manager
        identity = manager.import_identity()
        voice_token = manager.import_token()
        for line in lines:
            line['cached'] = await manager._cache.find_cached_audio(text=line['text'],**identity) is not None
        if voice_token != manager.import_token():
            raise ValueError('Voice settings changed; review again')
        self.reviews = {token:value for token,value in self.reviews.items() if self.clock()-value['at']<900}
        while len(self.reviews)>=8:
            self.reviews.pop(next(iter(self.reviews)))
        token = secrets.token_urlsafe(24)
        missing = {line['id'] for line in lines if not line['cached']}
        self.reviews[token] = {'at':self.clock(),'voice':voice_token,'digest':digest,
                              'cost_settings':self.cost_settings(),
                              'modes':list(modes),'missing':missing,'attempted':set(),'identity':identity}
        state = await manager._cache.snapshot(limit=0)
        return {'token':token,'lines':lines,'missing_count':len(missing),
                'voice':{'provider':identity['provider'], 'voice':manager._entry.options.get('elevenlabs_voice') or 'Provider default',
                         'revision':manager._entry.options.get('cache_revision','v1')},
                'maximum_characters':sum(line['characters'] for line in lines if line['id'] in missing),
                'cache_enabled':manager._entry.options.get('cache_enabled',True),
                'storage_available':state['storage_available'], 'usage':manager.budget_snapshot()}

    def cost_settings(self):
        options=self.manager._entry.options
        return (options.get('primary_daily_character_limit',0), options.get('primary_credit_estimate_per_character',0))

    async def prepare(self, token, line_id):
        async with self.lock:
            review = self.reviews.get(token)
            if not review or self.clock()-review['at']>=900:
                raise ValueError('Review expired; review the catalogue again')
            manager = self.manager
            lines, digest = await self.lines(review['modes'])
            if review['voice']!=manager.import_token() or review['digest']!=digest or review['cost_settings']!=self.cost_settings():
                raise ValueError('Voice settings or catalogue changed; review again')
            if not manager._entry.options.get('cache_enabled',True):
                raise ValueError('Enable the voice cache before preparing recordings')
            line = next((line for line in lines if line['id']==line_id),None)
            if line is None or line_id not in review['missing']:
                raise ValueError('This sentence was not approved as missing')
            identity = review['identity']
            cached = await manager._cache.find_cached_audio(text=line['text'],**identity)
            if cached is not None:
                manager._usage.record('elevenlabs_cached')
                return {'cached':True,'saved':True,'characters_requested':0}
            if line_id in review['attempted']:
                raise ValueError('This sentence was already attempted; review again before retrying')
            if not (await manager._cache.snapshot(limit=0))['storage_available']:
                raise ValueError('Voice cache storage is full; no generation requested')
            async def generate():
                if review['voice']!=manager.import_token() or review['cost_settings']!=self.cost_settings():
                    raise ValueError('Voice settings changed; review again')
                review['attempted'].add(line_id)
                return await manager._generate_audio(provider_entity_id=identity['provider'],
                    text=line['text'],language=identity['language'],options=identity['settings'])
            extension, audio, hit = await manager._cache.get_or_generate_audio(
                text=line['text'],**identity,generate=generate)
            manager._usage.record('elevenlabs_cached' if hit else 'elevenlabs_generated')
            saved = await manager._cache.find_cached_audio(text=line['text'],**identity) is not None
            return {'cached':hit,'saved':saved,'characters_requested':0 if hit else line['characters']}
