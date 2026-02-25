"""
Risk Fields Backfill Generator

Transforms thin risk assessment strings in safety_data into rich structured objects.
Permanently writes enriched data back to the source YAML file.

Applies to: materials, contaminants, compounds, settings domain source data

Fields transformed:
    fire_explosion_risk: "moderate" → {severity, description, mitigation}
    toxic_gas_risk:      "high"     → {severity, primary_hazards, description, mitigation}
    visibility_hazard:   "moderate" → {severity, description, source, mitigation}
    ppe_requirements:    (adds rationale field)
    ventilation_requirements: (adds rationale field)

Usage (via run.py or direct):
    from generation.backfill.risk_fields_backfill import RiskFieldsBackfillGenerator

    config = {
        'source_file': 'data/materials/Materials.yaml',
        'items_key': 'materials',
        'field': 'safety_data',
        'domain': 'materials',
        'dry_run': True,
    }
    generator = RiskFieldsBackfillGenerator(config)
    stats = generator.backfill_all()
"""

from typing import Any, Dict, List

from generation.backfill.base import BaseBackfillGenerator


# ---------------------------------------------------------------------------
# Static lookup tables (no hardcoded inline literals in populate())
# ---------------------------------------------------------------------------

FIRE_RISK_DESCRIPTIONS: Dict[str, str] = {
    'critical': 'Immediate ignition risk with pyrophoric materials or explosive vapor generation',
    'high': 'Flammable residues or combustible dust with significant fire/explosion potential',
    'moderate': 'Combustible materials present, risk elevated in confined spaces or high-power settings',
    'low': 'Minimal fire risk with standard precautions and adequate ventilation',
    'none': 'No significant fire or explosion risk identified',
}

FIRE_RISK_MITIGATION: Dict[str, str] = {
    'critical': 'Emergency protocols required. Fire extinguisher within 3m, fire watch mandatory, explosion-proof equipment',
    'high': 'Fire extinguisher within 10m, avoid enclosed spaces, monitor for hot spots, spark-resistant tools',
    'moderate': 'Fire extinguisher accessible, adequate ventilation, monitor substrate temperature',
    'low': 'Standard fire safety precautions, extinguisher available within 15m',
    'none': 'Standard workplace fire safety protocols',
}

VISIBILITY_IMPACT_DESCRIPTIONS: Dict[str, str] = {
    'critical': 'Complete visibility loss, dense smoke generation creating evacuation hazard',
    'high': 'Severe visibility reduction (60-80%), dense particulate or smoke generation',
    'moderate': 'Moderate visibility reduction (40-60%), significant particulate haze',
    'low': 'Light haze (20-40% reduction), minimal impact on sight lines',
    'none': 'No significant visibility impact',
}

VISIBILITY_MITIGATION: Dict[str, str] = {
    'critical': 'Emergency evacuation protocols, multiple exits accessible, evacuation lighting required',
    'high': 'Maintain clear evacuation routes, supplemental lighting, restrict operator movement',
    'moderate': 'Ensure clear sight lines, use source extraction, maintain awareness of surroundings',
    'low': 'Standard visibility precautions, adequate lighting',
    'none': 'No special visibility precautions required',
}

# Domains where safety_data is nested under laser_properties
_NESTED_SAFETY_DATA_DOMAINS = {'contaminants'}


class RiskFieldsBackfillGenerator(BaseBackfillGenerator):
    """
    Backfill generator that converts flat risk severity strings in safety_data
    into rich structured objects with severity, description, and mitigation.

    Also injects a `rationale` field into ppe_requirements and
    ventilation_requirements where one is absent.

    Config keys (in addition to base):
        domain (str): One of 'materials', 'contaminants', 'compounds', 'settings'.
                      Determines whether safety_data is addressed directly or via
                      the laser_properties wrapper used by contaminants.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        if 'domain' not in config:
            raise KeyError("RiskFieldsBackfillGenerator requires 'domain' in config")
        self._domain = config['domain']
        super().__init__(config)

    # ------------------------------------------------------------------
    # BaseBackfillGenerator interface
    # ------------------------------------------------------------------

    def _should_skip(self, item_data: Dict[str, Any]) -> bool:
        """Skip if fire_explosion_risk is already a structured dict (already enriched)."""
        safety = self._get_safety_data(item_data)
        if safety is None:
            return True  # No safety_data → nothing to enrich

        fire_risk = safety.get('fire_explosion_risk')
        if isinstance(fire_risk, dict):
            return True  # Already enriched

        # If there are no enrichable risk fields at all, skip
        has_string_risk = any(
            isinstance(safety.get(f), str)
            for f in ('fire_explosion_risk', 'toxic_gas_risk', 'visibility_hazard')
        )
        return not has_string_risk

    def populate(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich risk fields and add rationale to requirements sections.

        Returns the modified item_data dict.
        """
        safety = self._get_safety_data(item_data)
        if safety is None:
            return item_data

        fumes_generated: List[Dict] = safety.get('fumes_generated', [])
        particulate = safety.get('particulate_generation', {})
        respirable_fraction: float = particulate.get('respirable_fraction', 0.5)

        changes: List[str] = []

        # 1. fire_explosion_risk
        fire_current = safety.get('fire_explosion_risk')
        if isinstance(fire_current, str):
            safety['fire_explosion_risk'] = self._enrich_fire(fire_current)
            changes.append(f"fire_explosion_risk: '{fire_current}' → structured")

        # 2. toxic_gas_risk
        toxic_current = safety.get('toxic_gas_risk')
        if isinstance(toxic_current, str):
            safety['toxic_gas_risk'] = self._enrich_toxic(toxic_current, fumes_generated)
            changes.append(f"toxic_gas_risk: '{toxic_current}' → structured")

        # 3. visibility_hazard
        vis_current = safety.get('visibility_hazard')
        if isinstance(vis_current, str):
            safety['visibility_hazard'] = self._enrich_visibility(vis_current, respirable_fraction)
            changes.append(f"visibility_hazard: '{vis_current}' → structured")

        # 4. ppe_requirements rationale
        ppe = safety.get('ppe_requirements')
        if isinstance(ppe, dict) and 'rationale' not in ppe:
            ppe['rationale'] = self._ppe_rationale(safety)
            changes.append("ppe_requirements: added rationale")

        # 5. ventilation_requirements rationale
        vent = safety.get('ventilation_requirements')
        if isinstance(vent, dict) and 'rationale' not in vent:
            vent['rationale'] = self._ventilation_rationale(safety, vent)
            changes.append("ventilation_requirements: added rationale")

        if changes:
            for msg in changes:
                print(f"      • {msg}")

        return item_data

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_safety_data(self, item_data: Dict[str, Any]) -> Any:
        """Return the safety_data dict for this item, respecting domain nesting."""
        if self._domain in _NESTED_SAFETY_DATA_DOMAINS:
            laser = item_data.get('laser_properties', {})
            return laser.get('safety_data') if isinstance(laser, dict) else None
        return item_data.get('safety_data')

    def _severity(self, risk_field) -> str:
        """Safely extract severity string from a risk field (str or dict)."""
        if isinstance(risk_field, dict):
            return risk_field.get('severity', 'low')
        if isinstance(risk_field, str):
            return risk_field
        return 'low'

    # ---- field enrichers ------------------------------------------------

    def _enrich_fire(self, severity: str) -> Dict[str, str]:
        return {
            'severity': severity,
            'description': FIRE_RISK_DESCRIPTIONS.get(
                severity, f'Fire risk level: {severity}'
            ),
            'mitigation': FIRE_RISK_MITIGATION.get(
                severity, 'Consult fire safety professional'
            ),
        }

    def _enrich_toxic(
        self, severity: str, fumes_generated: List[Dict]
    ) -> Dict[str, Any]:
        primary_hazards = [
            {
                'compound': f.get('compound', 'Unknown'),
                'concentration_mg_m3': f.get('concentration_mg_m3', 'N/A'),
                'hazard_class': f.get('hazard_class', 'unknown'),
            }
            for f in fumes_generated
            if f.get('hazard_class') in {'carcinogenic', 'highly_toxic', 'toxic'}
        ][:5]

        return {
            'severity': severity,
            'primary_hazards': primary_hazards,
            'description': self._toxic_description(severity, primary_hazards),
            'mitigation': self._toxic_mitigation(severity, primary_hazards),
        }

    def _toxic_description(self, severity: str, hazards: List[Dict]) -> str:
        base = {
            'critical': 'Extremely toxic or lethal gas generation requiring immediate evacuation protocols',
            'high': 'Toxic gas generation requiring respiratory protection and continuous monitoring',
            'moderate': 'Irritant gas generation requiring respiratory protection',
            'low': 'Minimal gas generation, nuisance particulates only',
            'none': 'No significant toxic gas generation',
        }
        if not hazards:
            return base.get(severity, 'Unknown toxic gas risk level')

        names = [h['compound'] for h in hazards[:3]]
        if len(names) == 1:
            return f"{names[0]} generation detected - {severity} toxicity risk"
        if len(names) == 2:
            return f"{names[0]} and {names[1]} generation - multiple toxic compounds"
        return f"Multiple toxic compounds detected: {', '.join(names)} - requires enhanced protection"

    def _toxic_mitigation(self, severity: str, hazards: List[Dict]) -> str:
        base = {
            'critical': 'SCBA or supplied air required, continuous gas monitoring, emergency evacuation plan',
            'high': 'Full-face respirator with appropriate cartridges, gas detection system, medical monitoring',
            'moderate': 'Half-face or full-face respirator with organic vapor/particulate cartridges, adequate ventilation',
            'low': 'N95 or P100 respirator for particulate control, standard ventilation',
            'none': 'Standard respiratory protection for particulate control',
        }
        mitigation = base.get(severity, 'Consult industrial hygienist')

        carcinogenic = [
            h for h in hazards if h.get('hazard_class') == 'carcinogenic'
        ]
        if carcinogenic:
            compounds = ', '.join(h['compound'] for h in carcinogenic[:2])
            mitigation += f". WARNING: {compounds} - known carcinogen(s), minimize exposure"

        return mitigation

    def _enrich_visibility(
        self, severity: str, respirable_fraction: float
    ) -> Dict[str, str]:
        percentage = int(respirable_fraction * 100)
        return {
            'severity': severity,
            'description': VISIBILITY_IMPACT_DESCRIPTIONS.get(
                severity, f'Visibility hazard: {severity}'
            ),
            'source': (
                f'Respirable fraction: {respirable_fraction:.2f} '
                f'({percentage}% of particles <10μm)'
            ),
            'mitigation': VISIBILITY_MITIGATION.get(
                severity, 'Maintain adequate visibility'
            ),
            'related_field': 'particulate_generation.respirable_fraction',
        }

    # ---- rationale generators ------------------------------------------

    def _ppe_rationale(self, safety: Dict[str, Any]) -> str:
        ppe = safety.get('ppe_requirements', {})
        respiratory = ppe.get('respiratory', 'N/A')
        eye = ppe.get('eye_protection', 'N/A')
        skin = ppe.get('skin_protection', 'N/A')
        fire_sev = self._severity(safety.get('fire_explosion_risk', 'low'))
        toxic_sev = self._severity(safety.get('toxic_gas_risk', 'low'))

        protections = []
        if 'SCBA' in respiratory or 'Supplied Air' in respiratory:
            protections.append('critical toxic gas exposure')
        elif 'Full-Face' in respiratory:
            protections.append('toxic gas and particulate exposure')
        elif 'P100' in respiratory or 'Respirator' in respiratory:
            protections.append('hazardous particulate exposure')

        if 'Combination' in eye:
            protections.append('chemical splash and impact hazards')
        elif 'Face Shield' in eye:
            protections.append('splash and thermal hazards')
        elif 'Goggles' in eye:
            protections.append('particulate and vapor exposure')

        if 'Chemical-Resistant' in skin:
            protections.append('chemical contact')
        elif 'Full Body' in skin:
            protections.append('extensive contamination risk')
        elif fire_sev in ('critical', 'high'):
            protections.append('thermal hazards')

        if not protections:
            return 'Standard protection against workplace hazards'
        return f"Protects against {', '.join(protections)}"

    def _ventilation_rationale(
        self, safety: Dict[str, Any], vent: Dict[str, Any]
    ) -> str:
        fire_sev = self._severity(safety.get('fire_explosion_risk', 'low'))
        toxic_sev = self._severity(safety.get('toxic_gas_risk', 'low'))
        vis_sev = self._severity(safety.get('visibility_hazard', 'low'))

        severity_order = ['none', 'low', 'moderate', 'medium', 'high', 'critical']

        def _rank(s: str) -> int:
            try:
                return severity_order.index(s)
            except ValueError:
                return 0

        max_sev = max([fire_sev, toxic_sev, vis_sev], key=_rank)
        ach = vent.get('minimum_air_changes_per_hour', 10)
        filtration = vent.get('filtration_type', 'Mechanical')

        reasons = []
        if toxic_sev in ('critical', 'high'):
            reasons.append('toxic gas generation')
        if fire_sev in ('critical', 'high'):
            reasons.append('fire/explosion risk')
        if vis_sev in ('high', 'critical'):
            reasons.append('dense particulate generation')

        if not reasons:
            return f'Standard industrial ventilation ({ach} ACH) for particulate control'

        level = 'Enhanced' if max_sev in ('high', 'critical') else 'Adequate'
        return f"{level} ventilation required due to {', '.join(reasons)} - {ach} ACH with {filtration}"


# ---------------------------------------------------------------------------
# Registry self-registration
# ---------------------------------------------------------------------------

from generation.backfill.registry import BackfillRegistry  # noqa: E402

BackfillRegistry.register('risk_fields', RiskFieldsBackfillGenerator)
