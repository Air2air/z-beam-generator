import requests
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AIDetector:
    """AI Detection and scoring utilities with multiple providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.zerogpt_enabled = config.get("zerogpt_enabled", True)
        self.sapling_key = config.get("sapling_api_key")
        self.winston_key = config.get("winston_api_key")
        self.contentatscale_key = config.get("contentatscale_api_key")
        self.target_ai_score = config.get("target_ai_score", 30)
        
        logger.info("🤖 AI Detector initialized")
    
    def score_content(self, text: str) -> Dict[str, Any]:
        """Score content for AI detection across multiple services"""
        logger.info("🤖 SCORING AI DETECTION...")
        
        results = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "services": {},
            "summary": {}
        }
        
        # Test multiple services
        if self.zerogpt_enabled:
            results["services"]["zerogpt"] = self._check_zerogpt(text)
        
        if self.sapling_key:
            results["services"]["sapling"] = self._check_sapling(text)
        
        if self.winston_key:
            results["services"]["winston"] = self._check_winston(text)
        
        if self.contentatscale_key:
            results["services"]["contentatscale"] = self._check_contentatscale(text)
        
        # Calculate summary
        results["summary"] = self._calculate_summary(results["services"])
        
        # Log results
        self._log_results(results)
        
        return results
    
    def _check_zerogpt(self, text: str) -> Dict[str, Any]:
        """Check with ZeroGPT API (Free)"""
        logger.info("🔍 Checking ZeroGPT...")
        
        try:
            # ZeroGPT API endpoint
            url = "https://api.zerogpt.com/api/detect/detectText"
            
            # Load API key from environment
            import os
            api_key = os.getenv("ZEROGPT_API_KEY")
            
            if not api_key:
                logger.error("❌ ZEROGPT_API_KEY not found in environment")
                return {"success": False, "error": "No API key"}
            
            # Prepare headers and payload
            headers = {
                "Content-Type": "application/json",
                "ApiKey": api_key  # ZeroGPT uses 'ApiKey' header
            }
            
            payload = {
                "input_text": text[:5000]  # Limit to 5000 chars
            }
            
            logger.info(f"📡 Sending to ZeroGPT: {len(payload['input_text'])} chars")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            logger.info(f"🌐 ZeroGPT Response Status: {response.status_code}")
            logger.info(f"📨 ZeroGPT Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"📊 ZeroGPT Raw Result: {result}")
                
                # Extract AI score
                ai_score = result.get("fakePercentage", 0)
                human_score = 100 - ai_score
                
                logger.info(f"🎯 ZeroGPT AI Score: {ai_score}%")
                
                return {
                    "success": True,
                    "ai_probability": ai_score,
                    "human_probability": human_score,
                    "is_human": result.get("isHuman", False),
                    "service": "ZeroGPT",
                    "raw_response": result  # Debug info
                }
            else:
                logger.error(f"❌ ZeroGPT API error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            logger.error(f"❌ ZeroGPT error: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_sapling(self, text: str) -> Dict[str, Any]:
        """Check with Sapling AI Detector"""
        logger.info("🔍 Checking Sapling...")
        
        try:
            url = "https://api.sapling.ai/api/v1/aidetect"
            
            response = requests.post(url, json={
                "key": self.sapling_key,
                "text": text[:5000]
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_score = result.get("score", 0) * 100
                
                return {
                    "success": True,
                    "ai_probability": ai_score,
                    "human_probability": 100 - ai_score,
                    "service": "Sapling"
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Sapling error: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_winston(self, text: str) -> Dict[str, Any]:
        """Check with Winston AI"""
        logger.info("🔍 Checking Winston AI...")
        
        try:
            url = "https://api.winston.ai/v1/predict"
            
            headers = {
                "Authorization": f"Bearer {self.winston_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json={
                "text": text[:5000],
                "language": "en"
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_score = result.get("prediction", 0) * 100
                
                return {
                    "success": True,
                    "ai_probability": ai_score,
                    "human_probability": 100 - ai_score,
                    "service": "Winston"
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Winston error: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_contentatscale(self, text: str) -> Dict[str, Any]:
        """Check with Content at Scale AI Detector"""
        logger.info("🔍 Checking Content at Scale...")
        
        try:
            url = "https://api.contentatscale.ai/detector"
            
            headers = {
                "Authorization": f"Bearer {self.contentatscale_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json={
                "content": text[:5000]
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_score = result.get("ai_probability", 0) * 100
                
                return {
                    "success": True,
                    "ai_probability": ai_score,
                    "human_probability": 100 - ai_score,
                    "service": "Content at Scale"
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Content at Scale error: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_summary(self, services: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate summary statistics from all services"""
        successful_services = [s for s in services.values() if s.get("success", False)]
        
        if not successful_services:
            return {
                "average_ai_score": 0,
                "average_human_score": 0,
                "passed_threshold": False,
                "services_count": 0
            }
        
        ai_scores = [s["ai_probability"] for s in successful_services]
        human_scores = [s["human_probability"] for s in successful_services]
        
        avg_ai = sum(ai_scores) / len(ai_scores)
        avg_human = sum(human_scores) / len(human_scores)
        
        return {
            "average_ai_score": avg_ai,
            "average_human_score": avg_human,
            "passed_threshold": avg_ai < self.target_ai_score,
            "services_count": len(successful_services),
            "min_ai_score": min(ai_scores),
            "max_ai_score": max(ai_scores)
        }
    
    def _log_results(self, results: Dict[str, Any]) -> None:
        """Log detection results"""
        logger.info("🤖 AI DETECTION RESULTS:")
        logger.info(f"📊 Text: {results['word_count']} words, {results['text_length']} chars")
        
        for service_name, service_result in results["services"].items():
            if service_result.get("success", False):
                ai_score = service_result["ai_probability"]
                logger.info(f"🔍 {service_name}: {ai_score:.1f}% AI detected")
            else:
                logger.warning(f"❌ {service_name}: Failed - {service_result.get('error', 'Unknown error')}")
        
        summary = results["summary"]
        if summary["services_count"] > 0:
            logger.info(f"📈 AVERAGE: {summary['average_ai_score']:.1f}% AI ({summary['services_count']} services)")
            
            if summary["passed_threshold"]:
                logger.info(f"✅ PASSED threshold (<{self.target_ai_score}%)")
            else:
                logger.warning(f"❌ FAILED threshold (≥{self.target_ai_score}%)")
        else:
            logger.error("❌ No services returned valid results")
    
    def print_detailed_report(self, results: Dict[str, Any]) -> None:
        """Print a detailed report of detection results"""
        print("\n" + "="*60)
        print("🤖 AI DETECTION REPORT")
        print("="*60)
        
        print(f"📊 Content: {results['word_count']} words, {results['text_length']} characters")
        print(f"🎯 Target AI Score: <{self.target_ai_score}%")
        print()
        
        # Individual service results
        print("📋 SERVICE RESULTS:")
        for service_name, service_result in results["services"].items():
            if service_result.get("success", False):
                ai_score = service_result["ai_probability"]
                status = "✅ PASS" if ai_score < self.target_ai_score else "❌ FAIL"
                print(f"  {service_name:15} {ai_score:6.1f}% AI  {status}")
            else:
                print(f"  {service_name:15} {'ERROR':>6}    ❌ {service_result.get('error', 'Unknown')}")
        
        print()
        
        # Summary
        summary = results["summary"]
        if summary["services_count"] > 0:
            print("📈 SUMMARY:")
            print(f"  Average AI Score: {summary['average_ai_score']:.1f}%")
            print(f"  Range: {summary['min_ai_score']:.1f}% - {summary['max_ai_score']:.1f}%")
            print(f"  Services Used: {summary['services_count']}")
            
            if summary["passed_threshold"]:
                print(f"  🎉 OVERALL RESULT: ✅ PASSED (<{self.target_ai_score}%)")
            else:
                print(f"  ⚠️  OVERALL RESULT: ❌ FAILED (≥{self.target_ai_score}%)")
        else:
            print("❌ No valid results from any service")
        
        print("="*60)

# Free alternative using local heuristics
class LocalAIDetector:
    """Local AI detection using heuristics (no API required)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target_ai_score = config.get("target_ai_score", 30)
        
    def score_content(self, text: str) -> Dict[str, Any]:
        """Score content using local heuristics"""
        logger.info("🔍 Running local AI detection heuristics...")
        
        # AI-typical patterns
        ai_patterns = [
            "furthermore", "moreover", "additionally", "consequently",
            "in conclusion", "to summarize", "it is important to note",
            "it should be noted", "it is worth mentioning",
            "comprehensive", "innovative", "cutting-edge", "state-of-the-art",
            "robust", "sophisticated", "paramount", "crucial",
            "in the realm of", "emerges as", "plays a pivotal role"
        ]
        
        human_patterns = [
            "i think", "i believe", "in my experience", "from what i've seen",
            "honestly", "actually", "basically", "pretty much",
            "it's", "don't", "can't", "won't", "here's the thing",
            "the way i see it", "if you ask me"
        ]
        
        text_lower = text.lower()
        words = text_lower.split()
        
        # Calculate scores
        ai_matches = sum(1 for pattern in ai_patterns if pattern in text_lower)
        human_matches = sum(1 for pattern in human_patterns if pattern in text_lower)
        
        # Sentence length analysis
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Heuristic scoring
        ai_score = min(100, (ai_matches * 10) + max(0, (avg_sentence_length - 20) * 2))
        human_score = min(100, (human_matches * 15) + max(0, (25 - avg_sentence_length) * 3))
        
        # Normalize
        total = ai_score + human_score
        if total > 0:
            ai_probability = (ai_score / total) * 100
            human_probability = (human_score / total) * 100
        else:
            ai_probability = 50
            human_probability = 50
        
        return {
            "text_length": len(text),
            "word_count": len(words),
            "services": {
                "local_heuristics": {
                    "success": True,
                    "ai_probability": ai_probability,
                    "human_probability": human_probability,
                    "service": "Local Heuristics",
                    "ai_patterns_found": ai_matches,
                    "human_patterns_found": human_matches,
                    "avg_sentence_length": avg_sentence_length
                }
            },
            "summary": {
                "average_ai_score": ai_probability,
                "average_human_score": human_probability,
                "passed_threshold": ai_probability < self.target_ai_score,
                "services_count": 1
            }
        }