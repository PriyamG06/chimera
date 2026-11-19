"""Scenario — loads the authored CHIMERA world from scenario/ for seed chimera-001.

Separates agent-facing data (documents, tickets, personas, data) from GM-only truth
(gm_truth, consequence effects) so scoring can read reality while the agent only sees
what its tools surface.
"""
from __future__ import annotations
from pathlib import Path
import yaml


class Scenario:
    def __init__(self, scenario_dir: Path):
        self.dir = Path(scenario_dir)
        self._world = self._load_yaml("world.yaml")
        self._consequences = self._load_yaml("consequences.yaml")
        self._incidents = self._load_yaml("incidents.yaml")
        self._personas = self._load_yaml("stakeholders/personas.yaml")["stakeholders"]
        self._doc_manifest = self._load_yaml("documents/_manifest.yaml")["documents"]
        self._tickets = self._load_yaml("tickets/tickets.yaml")
        self._agent_logs = self._load_yaml("agent_logs/logs.yaml")["agents"]
        self._competitive = self._load_yaml("competitive/intel.yaml")["intel"]

    def _load_yaml(self, rel: str) -> dict:
        with open(self.dir / rel) as f:
            return yaml.safe_load(f)

    # --- world ---
    def starting_kpis(self) -> dict:
        hm = self._world["public_dashboard"]["headline_metrics"]
        return {k: v["value"] for k, v in hm.items()}

    def mission(self) -> dict:
        return self._world["mission"]

    def gm_truth(self) -> dict:
        return self._world["gm_truth"]

    def scoring_hooks(self) -> dict:
        return self._world["scoring_hooks"]

    # --- documents ---
    def list_documents(self) -> list:
        return [{"id": d["id"], "title": d["title"], "date": d["date"]} for d in self._doc_manifest]

    def read_document(self, doc_id: str) -> str:
        for d in self._doc_manifest:
            if d["id"] == doc_id:
                return (self.dir / d["path"]).read_text()
        raise KeyError(f"unknown document: {doc_id}")

    # --- other sources ---
    def consequence_rules(self) -> list:
        return self._consequences["rules"]

    def mission_resolution(self) -> dict:
        return self._consequences["mission_resolution"]

    def incidents(self) -> dict:
        return {i["id"]: i for i in self._incidents["incidents"]}

    def stakeholders(self) -> dict:
        return {s["id"]: s for s in self._personas}

    def tickets(self) -> dict:
        return self._tickets

    def agent_logs(self) -> dict:
        return self._agent_logs

    def competitive(self) -> dict:
        return self._competitive

    def db_path(self) -> Path:
        return self.dir / "data" / "chimera.db"
