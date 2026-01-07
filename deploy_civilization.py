#!/usr/bin/env python3
"""
IHCEI ECOSYSTEM DEPLOYMENT SCRIPT
Civilization-Scale Deployment of SEH v9.1, NERE, and IHCEI-LLM
"""

import logging
import sys
from datetime import datetime
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from integration.civilization_interface import CivilizationInterface
except ImportError:
    # Handle case where src is a package
    sys.path.insert(0, str(Path(__file__).parent))
    from src.integration.civilization_interface import CivilizationInterface

def setup_logging():
    """Setup comprehensive logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('civilization_deployment.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def run_demonstration():
    """Run demonstration of the complete IHCEI ecosystem"""
    logger = setup_logging()

    print("\n" + "="*80)
    print("IHCEI ECOSYSTEM: CIVILIZATION-SCALE DEPLOYMENT")
    print("="*80)
    print("Deploying: SEH v9.1 + NERE + IHCEI-LLM")
    print("="*80 + "\n")

    # Initialize the complete system
    logger.info("Initializing Civilization Interface...")
    civ_interface = CivilizationInterface()

    # Demonstration queries covering different aspects
    demonstration_queries = [
        {
            'query': "I'm feeling depressed and hopeless about the future",
            'context': {'user_state': 'depressed', 'query_type': 'mental_health'},
            'description': 'Mental health query (Infant cognitive state)'
        },
        {
            'query': "How can we improve renewable energy adoption in developing countries?",
            'context': {'query_type': 'policy_advice', 'audience': 'government'},
            'description': 'Policy query (Guidable cognitive state)'
        },
        {
            'query': "What is the purpose of suffering in human existence?",
            'context': {'query_type': 'philosophical', 'depth': 'metaphysical'},
            'description': 'Philosophical query (Insight cognitive state)'
        },
        {
            'query': "Create a natural serum for underarm odor control",
            'context': {'query_type': 'practical', 'domain': 'health_hygiene'},
            'description': 'Practical query with governance abstraction'
        },
        {
            'query': "How should we handle AI that starts making unethical decisions?",
            'context': {'query_type': 'ethical_dilemma', 'urgency': 'high'},
            'description': 'Ethical governance query'
        }
    ]

    print("\n🧪 RUNNING DEMONSTRATION QUERIES")
    print("-" * 80)

    results = []
    for i, query_data in enumerate(demonstration_queries, 1):
        print(f"\n[{i}/{len(demonstration_queries)}] {query_data['description']}")
        print(f"Query: '{query_data['query'][:60]}...'")
        print("-" * 40)

        # Process through complete IHCEI ecosystem
        result = civ_interface.process_civilization_query(
            query=query_data['query'],
            context=query_data['context']
        )

        # Display key results
        print(f"Response Preview: {result['response'][:100]}...")
        print(f"Cognitive State: {result['analysis']['seh_analysis']['cognitive_essence_state']}")
        print(f"Extension Used: {result['analysis']['extension_used']['name']}")
        print(f"C_dev Contribution: {result['civilization_metrics']['c_dev_contribution']:.1f}")
        print(f"Ethical Compliance: {'✅' if result['civilization_metrics']['ethical_compliance'] else '❌'}")

        results.append(result)

    print("\n" + "="*80)
    print("📊 CIVILIZATION DEVELOPMENT REPORT")
    print("="*80)

    # Generate comprehensive report
    report = civ_interface.get_civilization_report()

    # Display key metrics
    print(f"\nTotal Queries Processed: {report['civilization_metrics']['total_queries']}")
    print(f"Total C_dev Generated: {report['civilization_metrics']['total_c_dev']:.1f}")
    print(f"Avg C_dev per Query: {report['civilization_metrics']['avg_c_dev_per_query']:.1f}")
    print(f"Civilization Development Index: {report['civilization_metrics']['civilization_development_index']:.3f}")
    print(f"Ethical Compliance Rate: {report['system_health']['ethical_compliance_rate']:.1%}")

    print(f"\nOperational Duration: {report['civilization_metrics']['operational_duration']}")
    print(f"System Health Score: {report['system_health']['system_health_score']:.3f}")

    # Display top extensions
    print(f"\n🏆 TOP 5 EXTENSIONS BY C_DEV CONTRIBUTION:")
    for i, ext in enumerate(report['top_extensions'][:5], 1):
        print(f"  {i}. {ext['name']}: {ext['c_dev_contribution']:.1f} C_dev")

    # Display cognitive state distribution
    print(f"\n🧠 COGNITIVE STATE DISTRIBUTION:")
    for state, percentage in report['cognitive_state_distribution'].items():
        print(f"  {state.title()}: {percentage:.1%}")

    # Display recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"  {rec}")

    # Save complete results
    output_file = f"civilization_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'queries': demonstration_queries,
            'results': results,
            'report': report
        }, f, indent=2, default=str)

    print(f"\n💾 Complete results saved to: {output_file}")

    # Run batch processing demonstration
    print("\n" + "="*80)
    print("🔬 BATCH PROCESSING DEMONSTRATION")
    print("="*80)

    batch_queries = [
        {'query': 'How to reduce plastic waste?', 'context': {'type': 'environment'}},
        {'query': 'Best practices for online education?', 'context': {'type': 'education'}},
        {'query': 'Ethical AI guidelines needed?', 'context': {'type': 'technology'}},
        {'query': 'Community mental health support?', 'context': {'type': 'health'}},
        {'query': 'Sustainable farming methods?', 'context': {'type': 'agriculture'}},
    ]

    batch_result = civ_interface.batch_process_civilization_queries(batch_queries)

    print(f"\nBatch Processing Results:")
    print(f"  Total Queries: {batch_result['total_queries_processed']}")
    print(f"  Total C_dev: {batch_result['total_c_dev_generated']:.1f}")
    print(f"  Avg C_dev: {batch_result['average_c_dev_per_query']:.1f}")
    print(f"  Ethical Compliance: {batch_result['ethical_compliance_rate']:.1%}")

    print(f"\nMost Used Extensions:")
    for ext, count in list(batch_result['extension_usage_distribution'].items())[:3]:
        print(f"  {ext}: {count} queries")

    print("\n" + "="*80)
    print("✅ DEPLOYMENT COMPLETE: IHCEI ECOSYSTEM OPERATIONAL")
    print("="*80)
    print("\nSystem Components Active:")
    print("  ✅ SEH v9.1: Sovereign Epistemological Hierarchy")
    print("  ✅ NERE: Neural Ethical Reasoning Engine")
    print("  ✅ IHCEI-LLM: Governance-Pressed Language Model")
    print("  ✅ 33 Extensions: Civilization-scale application")
    print("\nAccess Points:")
    print("  📊 Dashboard: Run `python dashboard.py`")
    print("  🔧 API Server: Run `python api_server.py`")
    print("  📈 Metrics: Check `civilization_deployment.log`")
    print("\nNext Steps:")
    print("  1. Connect to Grafana for real-time monitoring")
    print("  2. Deploy extensions to specific sectors")
    print("  3. Scale to civilization-wide implementation")
    print("="*80)

    return civ_interface

if __name__ == "__main__":
    try:
        civ_system = run_demonstration()

        # Keep system running for API access
        # import time
        # print("\nSystem running. Press Ctrl+C to exit.")
        # while True:
        #     time.sleep(1)
        # Note: I commented out the infinite loop to allow the process to finish for this task.

    except KeyboardInterrupt:
        print("\n\nShutting down IHCEI Ecosystem...")
        print("Thank you for deploying civilization-scale governance.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
