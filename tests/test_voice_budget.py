"""Durable speech budget limits, including concurrency and storage faults."""
import asyncio
import copy
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('voice_budget_fixture',Path(__file__).resolve().parents[1]/'custom_components'/'jarvis_local'/'voice_budget.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class Store:
    def __init__(self):self.saved=None;self.fail=False
    async def async_load(self):return copy.deepcopy(self.saved)
    async def async_save(self,data):
        if self.fail:raise OSError('storage unavailable')
        self.saved=copy.deepcopy(data)

class BudgetTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.day='2026-10-31';self.store=Store()
        self.budget=module.VoiceBudget(self.store,today=lambda:self.day)

    async def test_restart_preserves_reservations_and_estimates(self):
        await self.budget.reserve('hello','primary',10)
        restored=module.VoiceBudget(self.store,today=lambda:self.day)
        await restored.load()
        value=restored.snapshot(10,0.5)
        self.assertEqual(value['primary_characters'],5)
        self.assertEqual(value['remaining_characters'],5)
        self.assertEqual(value['estimated_credits'],2.5)
        self.assertNotIn('hello',str(self.store.saved))

    async def test_concurrent_requests_cannot_overspend_and_fallback_remains_available(self):
        results=await asyncio.gather(self.budget.reserve('hello','primary',5),
                                     self.budget.reserve('again','primary',5),return_exceptions=True)
        self.assertEqual(sum(isinstance(r,ValueError) for r in results),1)
        self.assertEqual(self.budget.snapshot(5)['primary_attempts'],1)
        await self.budget.reserve('local','fallback')
        self.assertEqual(self.budget.snapshot(5)['fallback_attempts'],1)

    async def test_new_utc_day_resets_but_clock_rollback_does_not(self):
        await self.budget.reserve('hello','primary',5)
        self.day='2026-10-30'
        with self.assertRaises(ValueError):await self.budget.reserve('x','primary',5)
        self.day='2026-11-01'
        await self.budget.reserve('x','primary',5)
        self.assertEqual(self.budget.snapshot(5)['primary_characters'],1)

    async def test_storage_failure_blocks_primary_before_any_request(self):
        self.store.fail=True
        with self.assertRaises(ValueError):await self.budget.reserve('hello','primary',10)
        self.assertFalse(self.budget.snapshot()['storage_available'])
        await self.budget.reserve('local','fallback')
        self.assertEqual(self.budget.snapshot()['primary_attempts'],0)

    async def test_corrupt_store_is_not_repaired_by_fallback_or_reset_to_free_allowance(self):
        self.store.saved={'bad':'data'}
        await self.budget.load()
        with self.assertRaises(ValueError):await self.budget.reserve('hello','primary',10)
        await self.budget.reserve('local','fallback')
        self.assertEqual(self.store.saved,{'bad':'data'})

    async def test_invalid_limits_and_unknown_credit_rate(self):
        for limit in (-1,True,1.5,'10'):
            with self.assertRaises(ValueError):await self.budget.reserve('x','primary',limit)
        self.assertIsNone(self.budget.snapshot()['estimated_credits'])
