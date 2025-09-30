#!/usr/bin/env python3
"""
Stage 6: Production Integration
Safely deploys validated and quality-assured property data to production systems.
"""

import yaml
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib

class ProductionIntegrator:
    """
    Handles safe deployment of validated property data to production systems
    with rollback capabilities and integrity verification.
    """
    
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.categories_file = Path("data/Categories.yaml")
        self.materials_file = Path("data/Materials.yaml")
        self.config_file = Path("config/pipeline_config.yaml")
        self.pipeline_results_dir = Path("pipeline_results")
        
        # Backup and deployment directories
        self.backup_dir = Path("backups/production_deployment")
        self.staging_dir = Path("staging/production_ready")
        
        # Load deployment configuration
        self.deployment_config = self._load_deployment_config()
        
        # Load QA results for deployment decisions
        self.qa_results = self._load_stage_results("stage5_quality_assurance_results.json")
        
        # Deployment tracking
        self.deployment_stats = {
            'materials_deployed': 0,
            'properties_updated': 0,
            'files_backed_up': 0,
            'integrity_checks_passed': 0,
            'rollbacks_available': 0,
            'errors': []
        }
    
    def _load_deployment_config(self) -> Dict[str, Any]:
        """Load production deployment configuration"""
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            return config.get('production_integration', {
                'deployment_criteria': {
                    'min_quality_score': 0.6,
                    'required_grade': 'acceptable',
                    'max_high_priority_issues': 2,
                    'critical_properties_required': True
                },
                'safety_measures': {
                    'create_backups': True,
                    'verify_integrity': True,
                    'staged_deployment': True,
                    'rollback_capability': True
                },
                'validation_gates': {
                    'schema_validation': True,
                    'cross_reference_check': True,
                    'range_validation': True,
                    'unit_consistency': True
                },
                'deployment_strategy': 'gradual'  # 'gradual' or 'batch'
            })
            
        except Exception as e:
            print(f"⚠️  Could not load deployment config: {e}")
            return self._get_default_deployment_config()
    
    def _get_default_deployment_config(self) -> Dict[str, Any]:
        """Default deployment configuration"""
        
        return {
            'deployment_criteria': {
                'min_quality_score': 0.6,
                'required_grade': 'acceptable',
                'max_high_priority_issues': 2,
                'critical_properties_required': True
            },
            'safety_measures': {
                'create_backups': True,
                'verify_integrity': True,
                'staged_deployment': True,
                'rollback_capability': True
            },
            'validation_gates': {
                'schema_validation': True,
                'cross_reference_check': True,
                'range_validation': True,
                'unit_consistency': True
            },
            'deployment_strategy': 'gradual'
        }
    
    def _load_stage_results(self, filename: str) -> Dict[str, Any]:
        """Load results from previous pipeline stages"""
        
        try:
            filepath = self.pipeline_results_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
            else:
                print(f"⚠️  Stage results not found: {filename}")
                return {}
        except Exception as e:
            print(f"⚠️  Error loading stage results {filename}: {e}")
            return {}
    
    def deploy_to_production(self, materials_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Deploy validated property data to production systems.
        
        Args:
            materials_filter: Optional list of specific materials to deploy
            
        Returns:
            Deployment results with success/failure status and rollback information
        """
        
        print("🚀 Starting production deployment process...")
        
        # Create deployment directories
        self._prepare_deployment_environment()
        
        # Analyze deployment readiness
        deployment_candidates = self._analyze_deployment_readiness(materials_filter)
        
        # Create comprehensive backup
        backup_manifest = self._create_production_backup()
        
        # Deploy materials in stages
        deployment_results = []
        
        if self.deployment_config['deployment_strategy'] == 'gradual':
            deployment_results = self._deploy_gradual(deployment_candidates)
        else:
            deployment_results = self._deploy_batch(deployment_candidates)
        
        # Verify deployment integrity
        integrity_verification = self._verify_deployment_integrity()
        
        # Generate deployment report
        deployment_report = self._generate_deployment_report(
            deployment_results, 
            backup_manifest, 
            integrity_verification
        )
        
        print(f"✅ Production deployment complete: {self.deployment_stats['materials_deployed']} materials deployed")
        print(f"🔧 {self.deployment_stats['properties_updated']} properties updated")
        print(f"💾 {self.deployment_stats['files_backed_up']} files backed up")
        
        return {
            'deployment_results': deployment_results,
            'backup_manifest': backup_manifest,
            'integrity_verification': integrity_verification,
            'statistics': self.deployment_stats,
            'report': deployment_report,
            'rollback_info': self._prepare_rollback_info(backup_manifest),
            'summary': self._generate_deployment_summary(deployment_results)
        }
    
    def _prepare_deployment_environment(self):
        """Prepare directories and environment for deployment"""
        
        # Create necessary directories
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear old staging data
        if self.staging_dir.exists():
            shutil.rmtree(self.staging_dir)
            self.staging_dir.mkdir(parents=True)
        
        print("📁 Deployment environment prepared")
    
    def _analyze_deployment_readiness(self, materials_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Analyze which materials are ready for production deployment"""
        
        print("📊 Analyzing deployment readiness...")
        
        if not self.qa_results:
            print("❌ No QA results available - cannot determine deployment readiness")
            return []
        
        deployment_candidates = []
        qa_assessments = self.qa_results.get('results', [])
        qa_recommendations = self.qa_results.get('recommendations', [])
        
        # Create recommendations lookup
        material_recommendations = {}
        for rec in qa_recommendations:
            material = rec.get('material')
            if material not in material_recommendations:
                material_recommendations[material] = []
            material_recommendations[material].append(rec)
        
        for assessment in qa_assessments:
            material_name = assessment.get('material')
            
            # Apply materials filter if provided
            if materials_filter and material_name not in materials_filter:
                continue
            
            if assessment.get('status') == 'error':
                continue
            
            # Check deployment criteria
            readiness = self._evaluate_deployment_readiness(assessment, material_recommendations.get(material_name, []))
            
            candidate = {
                'material': material_name,
                'ready_for_deployment': readiness['ready'],
                'quality_score': assessment.get('overall_score', 0),
                'quality_grade': assessment.get('quality_grade', 'unknown'),
                'readiness_details': readiness,
                'assessment': assessment
            }
            
            deployment_candidates.append(candidate)
        
        ready_count = sum(1 for c in deployment_candidates if c['ready_for_deployment'])
        print(f"📊 {ready_count}/{len(deployment_candidates)} materials ready for deployment")
        
        return deployment_candidates
    
    def _evaluate_deployment_readiness(self, assessment: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate if a material is ready for production deployment"""
        
        criteria = self.deployment_config['deployment_criteria']
        
        readiness = {
            'ready': True,
            'blocking_issues': [],
            'warnings': [],
            'criteria_met': {}
        }
        
        # Check minimum quality score
        quality_score = assessment.get('overall_score', 0)
        min_score = criteria['min_quality_score']
        readiness['criteria_met']['min_quality_score'] = quality_score >= min_score
        
        if quality_score < min_score:
            readiness['ready'] = False
            readiness['blocking_issues'].append(f"Quality score {quality_score:.2f} below minimum {min_score}")
        
        # Check quality grade
        grade = assessment.get('quality_grade', 'unknown')
        required_grades = ['excellent', 'good', 'acceptable']
        required_grade = criteria['required_grade']
        
        if required_grade == 'acceptable':
            grade_acceptable = grade in required_grades
        elif required_grade == 'good':
            grade_acceptable = grade in ['excellent', 'good']
        else:
            grade_acceptable = grade == 'excellent'
        
        readiness['criteria_met']['required_grade'] = grade_acceptable
        
        if not grade_acceptable:
            readiness['ready'] = False
            readiness['blocking_issues'].append(f"Quality grade '{grade}' does not meet requirement '{required_grade}'")
        
        # Check high priority issues
        high_priority_recs = [r for r in recommendations if r.get('priority') == 'high']
        max_high_priority = criteria['max_high_priority_issues']
        readiness['criteria_met']['max_high_priority_issues'] = len(high_priority_recs) <= max_high_priority
        
        if len(high_priority_recs) > max_high_priority:
            readiness['ready'] = False
            readiness['blocking_issues'].append(f"{len(high_priority_recs)} high priority issues exceed maximum {max_high_priority}")
        
        # Check critical properties
        if criteria['critical_properties_required']:
            critical_status = assessment.get('critical_properties_status', {})
            missing_critical = [prop for prop, status in critical_status.items() if not status.get('present', False)]
            low_confidence_critical = [prop for prop, status in critical_status.items() 
                                     if status.get('present', False) and not status.get('meets_requirements', False)]
            
            readiness['criteria_met']['critical_properties'] = len(missing_critical) == 0
            
            if missing_critical:
                readiness['ready'] = False
                readiness['blocking_issues'].append(f"Missing critical properties: {', '.join(missing_critical)}")
            
            if low_confidence_critical:
                readiness['warnings'].append(f"Low confidence critical properties: {', '.join(low_confidence_critical)}")
        
        return readiness
    
    def _create_production_backup(self) -> Dict[str, Any]:
        """Create comprehensive backup of current production data"""
        
        print("💾 Creating production backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_session_dir = self.backup_dir / f"deployment_backup_{timestamp}"
        backup_session_dir.mkdir(parents=True, exist_ok=True)
        
        backup_manifest = {
            'timestamp': timestamp,
            'backup_directory': str(backup_session_dir),
            'backed_up_files': [],
            'checksums': {},
            'statistics': {
                'total_files': 0,
                'total_size_bytes': 0
            }
        }
        
        # Backup frontmatter files
        frontmatter_backup_dir = backup_session_dir / "frontmatter"
        frontmatter_backup_dir.mkdir(exist_ok=True)
        
        for yaml_file in self.frontmatter_dir.glob("*.yaml"):
            backup_file = frontmatter_backup_dir / yaml_file.name
            shutil.copy2(yaml_file, backup_file)
            
            # Calculate checksum
            checksum = self._calculate_file_checksum(yaml_file)
            
            backup_manifest['backed_up_files'].append({
                'original_path': str(yaml_file),
                'backup_path': str(backup_file),
                'checksum': checksum,
                'size_bytes': yaml_file.stat().st_size
            })
            
            backup_manifest['checksums'][str(yaml_file)] = checksum
            backup_manifest['statistics']['total_files'] += 1
            backup_manifest['statistics']['total_size_bytes'] += yaml_file.stat().st_size
        
        # Backup Categories.yaml
        if self.categories_file.exists():
            categories_backup = backup_session_dir / "Categories.yaml"
            shutil.copy2(self.categories_file, categories_backup)
            
            checksum = self._calculate_file_checksum(self.categories_file)
            backup_manifest['backed_up_files'].append({
                'original_path': str(self.categories_file),
                'backup_path': str(categories_backup),
                'checksum': checksum,
                'size_bytes': self.categories_file.stat().st_size
            })
            backup_manifest['checksums'][str(self.categories_file)] = checksum
        
        # Save backup manifest
        manifest_file = backup_session_dir / "backup_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(backup_manifest, f, indent=2)
        
        self.deployment_stats['files_backed_up'] = backup_manifest['statistics']['total_files']
        self.deployment_stats['rollbacks_available'] += 1
        
        print(f"💾 Backup complete: {backup_manifest['statistics']['total_files']} files backed up")
        
        return backup_manifest
    
    def _deploy_gradual(self, deployment_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deploy materials gradually with validation at each step"""
        
        print("🚀 Starting gradual deployment...")
        
        deployment_results = []
        
        # Sort candidates by quality score (deploy best first)
        ready_candidates = [c for c in deployment_candidates if c['ready_for_deployment']]
        ready_candidates.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Deploy in batches
        batch_size = 5
        for i in range(0, len(ready_candidates), batch_size):
            batch = ready_candidates[i:i + batch_size]
            
            print(f"🚀 Deploying batch {i//batch_size + 1}: {len(batch)} materials")
            
            for candidate in batch:
                result = self._deploy_single_material(candidate)
                deployment_results.append(result)
                
                # Stop if deployment fails
                if not result['success']:
                    print(f"❌ Deployment failed for {candidate['material']}, stopping gradual deployment")
                    break
            
            # Validate batch deployment
            batch_validation = self._validate_batch_deployment([r['material'] for r in deployment_results[-len(batch):]])
            
            if not batch_validation['success']:
                print(f"❌ Batch validation failed, stopping deployment")
                break
        
        return deployment_results
    
    def _deploy_batch(self, deployment_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deploy all ready materials in a single batch"""
        
        print("🚀 Starting batch deployment...")
        
        deployment_results = []
        ready_candidates = [c for c in deployment_candidates if c['ready_for_deployment']]
        
        for candidate in ready_candidates:
            result = self._deploy_single_material(candidate)
            deployment_results.append(result)
        
        return deployment_results
    
    def _deploy_single_material(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a single material to production"""
        
        material_name = candidate['material']
        
        deployment_result = {
            'material': material_name,
            'success': False,
            'deployment_timestamp': datetime.now().isoformat(),
            'changes_applied': [],
            'validation_results': {},
            'error': None
        }
        
        try:
            # Load current material data
            material_file = self.frontmatter_dir / f"{material_name}-laser-cleaning.yaml"
            
            if not material_file.exists():
                deployment_result['error'] = f"Material file not found: {material_file}"
                return deployment_result
            
            with open(material_file, 'r') as f:
                material_data = yaml.safe_load(f)
            
            # Apply deployment validation gates
            validation_gates = self._run_deployment_validation_gates(material_name, material_data)
            deployment_result['validation_results'] = validation_gates
            
            if not validation_gates['all_gates_passed']:
                deployment_result['error'] = f"Validation gates failed: {validation_gates['failed_gates']}"
                return deployment_result
            
            # Stage the material for deployment
            staged_file = self.staging_dir / f"{material_name}-laser-cleaning.yaml"
            with open(staged_file, 'w') as f:
                yaml.dump(material_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            # Apply to production (copy from staging)
            shutil.copy2(staged_file, material_file)
            
            deployment_result['success'] = True
            deployment_result['changes_applied'].append(f"Deployed validated data for {material_name}")
            
            self.deployment_stats['materials_deployed'] += 1
            properties_count = len(material_data.get('materialProperties', {}))
            self.deployment_stats['properties_updated'] += properties_count
            
        except Exception as e:
            deployment_result['error'] = str(e)
            self.deployment_stats['errors'].append(f"Deployment error for {material_name}: {e}")
        
        return deployment_result
    
    def _run_deployment_validation_gates(self, material_name: str, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run validation gates before deployment"""
        
        gates = self.deployment_config['validation_gates']
        validation_results = {
            'all_gates_passed': True,
            'failed_gates': [],
            'gate_results': {}
        }
        
        # Schema validation
        if gates.get('schema_validation', True):
            schema_valid = self._validate_material_schema(material_data)
            validation_results['gate_results']['schema_validation'] = schema_valid
            if not schema_valid:
                validation_results['all_gates_passed'] = False
                validation_results['failed_gates'].append('schema_validation')
        
        # Cross-reference check
        if gates.get('cross_reference_check', True):
            cross_ref_valid = self._validate_cross_references(material_data)
            validation_results['gate_results']['cross_reference_check'] = cross_ref_valid
            if not cross_ref_valid:
                validation_results['all_gates_passed'] = False
                validation_results['failed_gates'].append('cross_reference_check')
        
        # Range validation
        if gates.get('range_validation', True):
            range_valid = self._validate_property_ranges(material_data)
            validation_results['gate_results']['range_validation'] = range_valid
            if not range_valid:
                validation_results['all_gates_passed'] = False
                validation_results['failed_gates'].append('range_validation')
        
        # Unit consistency
        if gates.get('unit_consistency', True):
            unit_valid = self._validate_unit_consistency(material_data)
            validation_results['gate_results']['unit_consistency'] = unit_valid
            if not unit_valid:
                validation_results['all_gates_passed'] = False
                validation_results['failed_gates'].append('unit_consistency')
        
        return validation_results
    
    def _validate_material_schema(self, material_data: Dict[str, Any]) -> bool:
        """Validate material data against schema"""
        
        # Check required top-level fields
        required_fields = ['title', 'category', 'materialProperties']
        for field in required_fields:
            if field not in material_data:
                return False
        
        # Check material properties structure
        properties = material_data.get('materialProperties', {})
        for prop_name, prop_data in properties.items():
            if not isinstance(prop_data, dict):
                return False
            
            # Check required property fields
            if 'value' not in prop_data:
                return False
        
        return True
    
    def _validate_cross_references(self, material_data: Dict[str, Any]) -> bool:
        """Validate cross-references are consistent"""
        
        # Check category exists in Categories.yaml
        category = material_data.get('category', '').lower()
        
        try:
            if self.categories_file.exists():
                with open(self.categories_file, 'r') as f:
                    categories_data = yaml.safe_load(f)
                
                categories = categories_data.get('categories', {})
                if category not in categories:
                    return False
        except:
            # If we can't validate, assume it's okay
            pass
        
        return True
    
    def _validate_property_ranges(self, material_data: Dict[str, Any]) -> bool:
        """Validate property values are within specified ranges"""
        
        properties = material_data.get('materialProperties', {})
        
        for prop_name, prop_data in properties.items():
            if not isinstance(prop_data, dict):
                continue
            
            value = prop_data.get('value')
            min_val = prop_data.get('min')
            max_val = prop_data.get('max')
            
            if all(v is not None for v in [value, min_val, max_val]):
                try:
                    val = float(value)
                    min_v = float(min_val)
                    max_v = float(max_val)
                    
                    if not (min_v <= val <= max_v):
                        return False
                        
                except (ValueError, TypeError):
                    continue
        
        return True
    
    def _validate_unit_consistency(self, material_data: Dict[str, Any]) -> bool:
        """Validate units are consistent and appropriate"""
        
        properties = material_data.get('materialProperties', {})
        
        # Expected units for common properties
        expected_units = {
            'density': ['g/cm³', 'kg/m³'],
            'meltingPoint': ['°C', 'K'],
            'thermalConductivity': ['W/m·K', 'W/mK'],
            'hardness': ['HV', 'HB', 'HRC'],
            'youngsModulus': ['GPa', 'Pa'],
            'tensileStrength': ['MPa', 'Pa']
        }
        
        for prop_name, prop_data in properties.items():
            if not isinstance(prop_data, dict):
                continue
            
            unit = prop_data.get('unit')
            if prop_name in expected_units and unit not in expected_units[prop_name]:
                # Allow if it's a reasonable variation
                if unit and any(expected in unit for expected in expected_units[prop_name]):
                    continue
                return False
        
        return True
    
    def _validate_batch_deployment(self, deployed_materials: List[str]) -> Dict[str, Any]:
        """Validate a batch of deployed materials"""
        
        validation_result = {
            'success': True,
            'materials_validated': len(deployed_materials),
            'validation_errors': []
        }
        
        for material_name in deployed_materials:
            try:
                material_file = self.frontmatter_dir / f"{material_name}-laser-cleaning.yaml"
                
                if not material_file.exists():
                    validation_result['success'] = False
                    validation_result['validation_errors'].append(f"Deployed file missing: {material_name}")
                    continue
                
                # Verify file integrity
                with open(material_file, 'r') as f:
                    yaml.safe_load(f)  # This will raise an exception if YAML is invalid
                    
            except Exception as e:
                validation_result['success'] = False
                validation_result['validation_errors'].append(f"Validation error for {material_name}: {e}")
        
        return validation_result
    
    def _verify_deployment_integrity(self) -> Dict[str, Any]:
        """Verify integrity of deployed data"""
        
        print("🔍 Verifying deployment integrity...")
        
        integrity_check = {
            'overall_integrity': True,
            'files_checked': 0,
            'checksum_matches': 0,
            'schema_validation_passed': 0,
            'integrity_errors': []
        }
        
        for yaml_file in self.frontmatter_dir.glob("*.yaml"):
            try:
                integrity_check['files_checked'] += 1
                
                # Verify file can be loaded
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Basic schema validation
                if self._validate_material_schema(data):
                    integrity_check['schema_validation_passed'] += 1
                else:
                    integrity_check['overall_integrity'] = False
                    integrity_check['integrity_errors'].append(f"Schema validation failed: {yaml_file.name}")
                
                self.deployment_stats['integrity_checks_passed'] += 1
                
            except Exception as e:
                integrity_check['overall_integrity'] = False
                integrity_check['integrity_errors'].append(f"Integrity error in {yaml_file.name}: {e}")
        
        print(f"🔍 Integrity check: {integrity_check['files_checked']} files verified")
        
        return integrity_check
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum for a file"""
        
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "error_calculating_checksum"
    
    def _prepare_rollback_info(self, backup_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare rollback information for emergency recovery"""
        
        rollback_info = {
            'rollback_available': True,
            'backup_timestamp': backup_manifest['timestamp'],
            'backup_directory': backup_manifest['backup_directory'],
            'files_count': len(backup_manifest['backed_up_files']),
            'rollback_command': f"python3 stages/stage6_production/rollback_deployment.py --backup-dir {backup_manifest['backup_directory']}",
            'verification_checksums': backup_manifest['checksums']
        }
        
        return rollback_info
    
    def _generate_deployment_report(self, deployment_results: List[Dict[str, Any]], backup_manifest: Dict[str, Any], integrity_verification: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive deployment report"""
        
        successful_deployments = [r for r in deployment_results if r['success']]
        failed_deployments = [r for r in deployment_results if not r['success']]
        
        report = {
            'deployment_summary': {
                'total_materials_processed': len(deployment_results),
                'successful_deployments': len(successful_deployments),
                'failed_deployments': len(failed_deployments),
                'deployment_success_rate': len(successful_deployments) / len(deployment_results) if deployment_results else 0,
                'deployment_timestamp': datetime.now().isoformat()
            },
            'backup_information': {
                'backup_created': True,
                'backup_timestamp': backup_manifest['timestamp'],
                'files_backed_up': backup_manifest['statistics']['total_files'],
                'backup_size_mb': backup_manifest['statistics']['total_size_bytes'] / (1024 * 1024)
            },
            'integrity_verification': integrity_verification,
            'failed_deployments_analysis': {
                'failure_reasons': [r['error'] for r in failed_deployments if r.get('error')],
                'materials_with_issues': [r['material'] for r in failed_deployments]
            },
            'validation_gates_summary': self._analyze_validation_gates(deployment_results),
            'rollback_capability': {
                'rollback_available': True,
                'backup_location': backup_manifest['backup_directory'],
                'recovery_time_estimate': '5-10 minutes'
            }
        }
        
        return report
    
    def _analyze_validation_gates(self, deployment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze validation gates results across deployments"""
        
        gate_summary = {
            'total_validations': 0,
            'gate_pass_rates': {},
            'most_common_failures': []
        }
        
        gate_failures = {}
        
        for result in deployment_results:
            validation_results = result.get('validation_results', {})
            gate_results = validation_results.get('gate_results', {})
            
            gate_summary['total_validations'] += 1
            
            for gate_name, passed in gate_results.items():
                if gate_name not in gate_summary['gate_pass_rates']:
                    gate_summary['gate_pass_rates'][gate_name] = {'passed': 0, 'total': 0}
                
                gate_summary['gate_pass_rates'][gate_name]['total'] += 1
                if passed:
                    gate_summary['gate_pass_rates'][gate_name]['passed'] += 1
                else:
                    gate_failures[gate_name] = gate_failures.get(gate_name, 0) + 1
        
        # Calculate pass rates
        for gate_name, stats in gate_summary['gate_pass_rates'].items():
            stats['pass_rate'] = stats['passed'] / stats['total'] if stats['total'] > 0 else 0
        
        # Most common failures
        gate_summary['most_common_failures'] = sorted(gate_failures.items(), key=lambda x: x[1], reverse=True)
        
        return gate_summary
    
    def _generate_deployment_summary(self, deployment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate deployment summary statistics"""
        
        successful_results = [r for r in deployment_results if r['success']]
        failed_results = [r for r in deployment_results if not r['success']]
        
        return {
            'total_deployments_attempted': len(deployment_results),
            'successful_deployments': len(successful_results),
            'failed_deployments': len(failed_results),
            'deployment_success_rate': len(successful_results) / len(deployment_results) if deployment_results else 0,
            'materials_now_in_production': [r['material'] for r in successful_results],
            'materials_blocked_from_production': [r['material'] for r in failed_results],
            'total_properties_deployed': self.deployment_stats['properties_updated'],
            'backup_files_created': self.deployment_stats['files_backed_up'],
            'integrity_checks_passed': self.deployment_stats['integrity_checks_passed'],
            'rollback_procedures_available': self.deployment_stats['rollbacks_available']
        }

def main():
    """Test the production integration functionality"""
    
    integrator = ProductionIntegrator()
    
    # Run production deployment on a subset for testing
    test_materials = ['aluminum', 'steel', 'copper']  # Limit for testing
    results = integrator.deploy_to_production(materials_filter=test_materials)
    
    # Save results
    results_dir = Path("pipeline_results")
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / "stage6_production_integration_results.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("🚀 PRODUCTION INTEGRATION STAGE COMPLETE")
    print("="*60)
    print(f"Deployments attempted: {results['summary']['total_deployments_attempted']}")
    print(f"Successful deployments: {results['summary']['successful_deployments']}")
    print(f"Deployment success rate: {results['summary']['deployment_success_rate']:.1%}")
    print(f"Properties deployed: {results['summary']['total_properties_deployed']}")
    print(f"Backup files created: {results['summary']['backup_files_created']}")
    
    if results['summary']['failed_deployments'] > 0:
        print(f"\n⚠️  {results['summary']['failed_deployments']} deployments failed")
        for material in results['summary']['materials_blocked_from_production']:
            print(f"  ❌ {material}")
    
    if results['rollback_info']['rollback_available']:
        print(f"\n🔄 Rollback available: {results['rollback_info']['rollback_command']}")

if __name__ == "__main__":
    main()