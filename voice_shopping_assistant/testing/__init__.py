"""Testing utilities and sample data for voice shopping assistant"""

from .sample_catalog import (
    sample_catalog,
    get_sample_products,
    get_sample_product_by_id,
    get_sample_products_by_category,
    get_catalog_statistics,
    create_test_product_search,
    create_test_cart_manager
)

from .conversation_simulator import (
    ConversationSimulator,
    ConversationScenario,
    ConversationResult,
    SimulatedCommand,
    CommandResult,
    ScenarioBuilder,
    create_test_scenarios
)

from .test_runner import (
    EndToEndTestRunner,
    TestReport,
    MockNLPProcessor,
    MockResponseGenerator,
    run_end_to_end_tests
)

__all__ = [
    # Sample catalog
    'sample_catalog',
    'get_sample_products',
    'get_sample_product_by_id', 
    'get_sample_products_by_category',
    'get_catalog_statistics',
    'create_test_product_search',
    'create_test_cart_manager',
    
    # Conversation simulation
    'ConversationSimulator',
    'ConversationScenario',
    'ConversationResult',
    'SimulatedCommand',
    'CommandResult',
    'ScenarioBuilder',
    'create_test_scenarios',
    
    # Test runner
    'EndToEndTestRunner',
    'TestReport',
    'MockNLPProcessor',
    'MockResponseGenerator',
    'run_end_to_end_tests'
]