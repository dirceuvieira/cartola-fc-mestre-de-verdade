"""Supabase client helper for upserts used by the collector PoC.

This module provides a thin wrapper around supabase-py to perform upserts in bulk.
"""
from typing import Any, Dict, List
import logging
import os

from supabase import create_client

LOG = logging.getLogger("collector.supabase")


def create_supabase_client(url: str, key: str):
    if not url or not key:
        raise ValueError('SUPABASE_URL and SUPABASE_KEY are required')
    return create_client(url, key)


class SupabaseWriter:
    def __init__(self, client):
        self.client = client

    def upsert_atletas(self, atletas: List[Dict[str, Any]]):
        if not atletas:
            return
        try:
            res = self.client.table('atletas').upsert(atletas).execute()
            LOG.info('Upsert atletas: %s rows', len(atletas))
            return res
        except Exception:
            LOG.exception('Failed upsert_atletas')
            raise

    def upsert_precos(self, precos: List[Dict[str, Any]]):
        if not precos:
            return
        try:
            res = self.client.table('precos').upsert(precos).execute()
            LOG.info('Upsert precos: %s rows', len(precos))
            return res
        except Exception:
            LOG.exception('Failed upsert_precos')
            raise

    def upsert_pontuacoes(self, ponts: List[Dict[str, Any]]):
        if not ponts:
            return
        try:
            res = self.client.table('pontuacoes').upsert(ponts).execute()
            LOG.info('Upsert pontuacoes: %s rows', len(ponts))
            return res
        except Exception:
            LOG.exception('Failed upsert_pontuacoes')
            raise
