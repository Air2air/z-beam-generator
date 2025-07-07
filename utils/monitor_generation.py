#!/usr/bin/env python3
"""
Z-Beam Generation Monitor
Auto-kills hung generation processes to prevent infinite hangs
"""

import subprocess
import time
import sys
import signal
import os
from pathlib import Path

class GenerationMonitor:
    """Monitor and auto-kill hung generation processes"""
    
    def __init__(self, max_runtime=600, check_interval=10):
        self.max_runtime = max_runtime  # 10 minutes default
        self.check_interval = check_interval  # Check every 10 seconds
        self.project_root = Path(__file__).parent.parent
    
    def monitor_generation(self, script_name="run.py"):
        """Monitor generation process and kill if hung"""
        print(f"🔍 Starting monitored generation (max runtime: {self.max_runtime}s)")
        
        # Change to project directory
        os.chdir(self.project_root)
        
        # Start generation process
        process = subprocess.Popen(
            ['python', script_name], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        start_time = time.time()
        
        try:
            while process.poll() is None:  # While process is running
                runtime = time.time() - start_time
                
                if runtime > self.max_runtime:
                    print(f"❌ Process hung for {runtime:.0f}s - FORCE KILLING")
                    self._kill_process(process)
                    return -1  # Timeout exit code
                
                print(f"⏱️  Generation running for {runtime:.0f}s... (max: {self.max_runtime}s)")
                time.sleep(self.check_interval)
            
            # Process completed normally
            runtime = time.time() - start_time
            exit_code = process.returncode
            
            if exit_code == 0:
                print(f"✅ Generation completed successfully in {runtime:.0f}s")
            else:
                print(f"❌ Generation failed with exit code {exit_code} after {runtime:.0f}s")
            
            return exit_code
            
        except KeyboardInterrupt:
            print(f"\n🛑 User interrupted - killing generation process")
            self._kill_process(process)
            return -2  # User interrupt exit code
    
    def _kill_process(self, process):
        """Force kill a process with escalating methods"""
        try:
            # Try graceful termination first
            process.terminate()
            
            # Wait 5 seconds for graceful shutdown
            try:
                process.wait(timeout=5)
                print("✅ Process terminated gracefully")
                return
            except subprocess.TimeoutExpired:
                pass
            
            # Force kill if graceful didn't work
            process.kill()
            process.wait(timeout=5)
            print("💀 Process force killed")
            
        except Exception as e:
            print(f"❌ Error killing process: {e}")
            # Nuclear option - kill all Python processes (risky!)
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'] and 'run.py' in ' '.join(proc.info['cmdline']):
                        proc.terminate()
                        print(f"💀 Killed Python process {proc.info['pid']}")
                except:
                    pass

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor Z-Beam generation")
    parser.add_argument('--timeout', type=int, default=600, 
                       help='Max runtime in seconds (default: 600)')
    parser.add_argument('--interval', type=int, default=10,
                       help='Check interval in seconds (default: 10)')
    parser.add_argument('--script', default='run.py',
                       help='Script to monitor (default: run.py)')
    
    args = parser.parse_args()
    
    monitor = GenerationMonitor(
        max_runtime=args.timeout,
        check_interval=args.interval
    )
    
    exit_code = monitor.monitor_generation(args.script)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()