"""Conversation simulation framework for end-to-end testing"""

import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..models.core import (
    Product, CartItem, CartSummary, Intent, Entity, IntentType, EntityType,
    NLPResult, ProcessingResult
)
from ..interfaces import (
    NLPProcessorInterface, CartManagerInterface, ResponseGeneratorInterface
)


class ConversationStatus(Enum):
    """Status of conversation simulation"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CommandType(Enum):
    """Types of simulated commands"""
    ADD_ITEM = "add_item"
    REMOVE_ITEM = "remove_item"
    SEARCH_PRODUCT = "search_product"
    VIEW_CART = "view_cart"
    CHECKOUT = "checkout"
    CLEAR_CART = "clear_cart"
    HELP = "help"


@dataclass
class SimulatedCommand:
    """A simulated voice command for testing"""
    command_type: CommandType
    text: str
    expected_intent: IntentType
    expected_entities: List[Dict[str, Any]]
    expected_success: bool = True
    timeout_seconds: float = 5.0
    description: str = ""
    
    def __post_init__(self):
        if not self.description:
            self.description = f"{self.command_type.value}: {self.text}"


@dataclass
class CommandResult:
    """Result of executing a simulated command"""
    command: SimulatedCommand
    success: bool
    processing_time: float
    nlp_result: Optional[NLPResult] = None
    response_text: str = ""
    error_message: str = ""
    cart_state: Optional[CartSummary] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for reporting"""
        return {
            "command_type": self.command.command_type.value,
            "command_text": self.command.text,
            "expected_success": self.command.expected_success,
            "actual_success": self.success,
            "processing_time": self.processing_time,
            "response_text": self.response_text,
            "error_message": self.error_message,
            "cart_items": len(self.cart_state.items) if self.cart_state else 0,
            "cart_total": self.cart_state.total_price if self.cart_state else 0.0,
            "nlp_confidence": self.nlp_result.confidence_score if self.nlp_result else 0.0,
            "intent_match": (
                self.nlp_result.intent.type == self.command.expected_intent 
                if self.nlp_result else False
            )
        }


@dataclass
class ConversationScenario:
    """A complete conversation scenario for testing"""
    name: str
    description: str
    commands: List[SimulatedCommand]
    session_id: str = ""
    expected_final_cart_items: int = 0
    expected_final_cart_total: float = 0.0
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = f"test-{self.name.lower().replace(' ', '-')}-{int(time.time())}"


@dataclass
class ConversationResult:
    """Result of running a complete conversation scenario"""
    scenario: ConversationScenario
    status: ConversationStatus
    command_results: List[CommandResult] = field(default_factory=list)
    total_time: float = 0.0
    success_rate: float = 0.0
    error_count: int = 0
    final_cart_state: Optional[CartSummary] = None
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance and accuracy metrics"""
        if not self.command_results:
            return {}
        
        successful_commands = sum(1 for r in self.command_results if r.success)
        total_commands = len(self.command_results)
        
        # Intent accuracy
        correct_intents = sum(
            1 for r in self.command_results 
            if r.nlp_result and r.nlp_result.intent.type == r.command.expected_intent
        )
        intent_accuracy = correct_intents / total_commands if total_commands > 0 else 0.0
        
        # Processing time stats
        processing_times = [r.processing_time for r in self.command_results]
        avg_processing_time = sum(processing_times) / len(processing_times)
        max_processing_time = max(processing_times)
        
        # NLP confidence stats
        confidences = [
            r.nlp_result.confidence_score for r in self.command_results 
            if r.nlp_result
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "success_rate": successful_commands / total_commands,
            "intent_accuracy": intent_accuracy,
            "error_count": self.error_count,
            "total_time": self.total_time,
            "avg_processing_time": avg_processing_time,
            "max_processing_time": max_processing_time,
            "avg_nlp_confidence": avg_confidence,
            "final_cart_items": len(self.final_cart_state.items) if self.final_cart_state else 0,
            "final_cart_total": self.final_cart_state.total_price if self.final_cart_state else 0.0,
            "cart_goal_achieved": (
                self.final_cart_state and 
                len(self.final_cart_state.items) == self.scenario.expected_final_cart_items
            ) if self.scenario.expected_final_cart_items > 0 else True
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for reporting"""
        metrics = self.calculate_metrics()
        return {
            "scenario_name": self.scenario.name,
            "scenario_description": self.scenario.description,
            "status": self.status.value,
            "session_id": self.scenario.session_id,
            "metrics": metrics,
            "command_results": [r.to_dict() for r in self.command_results]
        }


class ConversationSimulator:
    """Framework for simulating complete shopping conversations"""
    
    def __init__(self, 
                 nlp_processor: NLPProcessorInterface,
                 cart_manager: CartManagerInterface,
                 response_generator: ResponseGeneratorInterface):
        """Initialize conversation simulator
        
        Args:
            nlp_processor: NLP processing interface
            cart_manager: Cart management interface
            response_generator: Response generation interface
        """
        self.nlp_processor = nlp_processor
        self.cart_manager = cart_manager
        self.response_generator = response_generator
        
        # Simulation state
        self.current_scenario: Optional[ConversationScenario] = None
        self.current_result: Optional[ConversationResult] = None
        
        # Performance tracking
        self.total_simulations = 0
        self.successful_simulations = 0
    
    def run_scenario(self, scenario: ConversationScenario) -> ConversationResult:
        """Run a complete conversation scenario
        
        Args:
            scenario: Conversation scenario to execute
            
        Returns:
            Complete conversation result with metrics
        """
        self.current_scenario = scenario
        self.current_result = ConversationResult(
            scenario=scenario,
            status=ConversationStatus.RUNNING
        )
        
        start_time = time.time()
        
        try:
            # Execute each command in sequence
            for command in scenario.commands:
                command_result = self._execute_command(command, scenario.session_id)
                self.current_result.command_results.append(command_result)
                
                if not command_result.success:
                    self.current_result.error_count += 1
                
                # Short delay between commands to simulate natural conversation
                time.sleep(0.1)
            
            # Get final cart state
            self.current_result.final_cart_state = self.cart_manager.get_cart_summary(
                scenario.session_id
            )
            
            # Calculate success rate
            successful_commands = sum(
                1 for r in self.current_result.command_results if r.success
            )
            total_commands = len(self.current_result.command_results)
            self.current_result.success_rate = (
                successful_commands / total_commands if total_commands > 0 else 0.0
            )
            
            # Determine overall status
            if self.current_result.success_rate >= 0.8:  # 80% success threshold
                self.current_result.status = ConversationStatus.COMPLETED
                self.successful_simulations += 1
            else:
                self.current_result.status = ConversationStatus.FAILED
            
        except Exception as e:
            self.current_result.status = ConversationStatus.FAILED
            self.current_result.error_count += 1
            # Add error to last command result if available
            if self.current_result.command_results:
                self.current_result.command_results[-1].error_message = str(e)
        
        finally:
            self.current_result.total_time = time.time() - start_time
            self.total_simulations += 1
        
        return self.current_result
    
    def run_multiple_scenarios(self, scenarios: List[ConversationScenario]) -> List[ConversationResult]:
        """Run multiple conversation scenarios
        
        Args:
            scenarios: List of scenarios to execute
            
        Returns:
            List of conversation results
        """
        results = []
        
        for scenario in scenarios:
            result = self.run_scenario(scenario)
            results.append(result)
            
            # Clean up session after each scenario
            self.cart_manager.cleanup_session(scenario.session_id)
        
        return results
    
    def _execute_command(self, command: SimulatedCommand, session_id: str) -> CommandResult:
        """Execute a single simulated command
        
        Args:
            command: Command to execute
            session_id: Session identifier
            
        Returns:
            Command execution result
        """
        start_time = time.time()
        
        try:
            # Process text with NLP
            nlp_result = self.nlp_processor.process_text(command.text, session_id)
            
            # Execute cart operations based on intent
            cart_result = None
            if nlp_result.intent.type == IntentType.ADD:
                cart_result = self._handle_add_command(nlp_result, session_id)
            elif nlp_result.intent.type == IntentType.REMOVE:
                cart_result = self._handle_remove_command(nlp_result, session_id)
            elif nlp_result.intent.type == IntentType.SEARCH:
                cart_result = self._handle_search_command(nlp_result, session_id)
            elif nlp_result.intent.type == IntentType.CHECKOUT:
                cart_result = self._handle_checkout_command(nlp_result, session_id)
            
            # Generate response
            response_text = self.response_generator.generate_response(
                nlp_result.intent, cart_result, None
            )
            
            # Get current cart state
            cart_state = self.cart_manager.get_cart_summary(session_id)
            
            processing_time = time.time() - start_time
            
            # Determine success based on expected vs actual results
            success = (
                nlp_result.intent.type == command.expected_intent and
                processing_time <= command.timeout_seconds and
                (cart_result is None or cart_result.success)
            )
            
            return CommandResult(
                command=command,
                success=success,
                processing_time=processing_time,
                nlp_result=nlp_result,
                response_text=response_text,
                cart_state=cart_state
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return CommandResult(
                command=command,
                success=False,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def _handle_add_command(self, nlp_result: NLPResult, session_id: str):
        """Handle ADD intent command"""
        # Extract product information from entities
        product_entities = nlp_result.intent.get_entities_by_type(EntityType.PRODUCT)
        quantity_entities = nlp_result.intent.get_entities_by_type(EntityType.QUANTITY)
        color_entities = nlp_result.intent.get_entities_by_type(EntityType.COLOR)
        size_entities = nlp_result.intent.get_entities_by_type(EntityType.SIZE)
        
        if not product_entities:
            return None
        
        # For simulation, we'll create mock items based on entities
        # In real implementation, this would search the product catalog
        items = []
        for product_entity in product_entities:
            # This is a simplified simulation - real implementation would
            # search for actual products matching the entity
            quantity = 1
            if quantity_entities:
                try:
                    quantity = int(quantity_entities[0].value)
                except ValueError:
                    quantity = 1
            
            # Create mock item specification
            item_spec = {
                'product_name': product_entity.value,
                'quantity': quantity,
                'color': color_entities[0].value if color_entities else None,
                'size': size_entities[0].value if size_entities else None
            }
            items.append(item_spec)
        
        # For simulation purposes, return a mock success result
        from ..interfaces import CartOperationResult
        return CartOperationResult(
            success=True,
            message=f"Added {len(items)} item(s) to cart"
        )
    
    def _handle_remove_command(self, nlp_result: NLPResult, session_id: str):
        """Handle REMOVE intent command"""
        # Extract removal criteria from entities
        criteria = {}
        
        product_entities = nlp_result.intent.get_entities_by_type(EntityType.PRODUCT)
        if product_entities:
            criteria['product_name'] = product_entities[0].value
        
        color_entities = nlp_result.intent.get_entities_by_type(EntityType.COLOR)
        if color_entities:
            criteria['color'] = color_entities[0].value
        
        size_entities = nlp_result.intent.get_entities_by_type(EntityType.SIZE)
        if size_entities:
            criteria['size'] = size_entities[0].value
        
        # For simulation, return mock result
        from ..interfaces import CartOperationResult
        return CartOperationResult(
            success=True,
            message="Removed item(s) from cart"
        )
    
    def _handle_search_command(self, nlp_result: NLPResult, session_id: str):
        """Handle SEARCH intent command"""
        # For simulation, return mock search result
        from ..interfaces import CartOperationResult
        return CartOperationResult(
            success=True,
            message="Found matching products"
        )
    
    def _handle_checkout_command(self, nlp_result: NLPResult, session_id: str):
        """Handle CHECKOUT intent command"""
        # For simulation, return mock checkout result
        from ..interfaces import CartOperationResult
        return CartOperationResult(
            success=True,
            message="Proceeding to checkout"
        )
    
    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get overall simulation statistics"""
        success_rate = (
            self.successful_simulations / self.total_simulations 
            if self.total_simulations > 0 else 0.0
        )
        
        return {
            "total_simulations": self.total_simulations,
            "successful_simulations": self.successful_simulations,
            "failed_simulations": self.total_simulations - self.successful_simulations,
            "overall_success_rate": success_rate
        }


class ScenarioBuilder:
    """Builder for creating conversation scenarios"""
    
    @staticmethod
    def create_basic_shopping_scenario() -> ConversationScenario:
        """Create a basic shopping scenario"""
        commands = [
            SimulatedCommand(
                command_type=CommandType.ADD_ITEM,
                text="add two red shirts to my cart",
                expected_intent=IntentType.ADD,
                expected_entities=[
                    {"type": "PRODUCT", "value": "shirts"},
                    {"type": "QUANTITY", "value": "two"},
                    {"type": "COLOR", "value": "red"}
                ],
                description="Add red shirts to cart"
            ),
            SimulatedCommand(
                command_type=CommandType.VIEW_CART,
                text="show me my cart",
                expected_intent=IntentType.SEARCH,
                expected_entities=[],
                description="View current cart contents"
            ),
            SimulatedCommand(
                command_type=CommandType.ADD_ITEM,
                text="add blue jeans size 32",
                expected_intent=IntentType.ADD,
                expected_entities=[
                    {"type": "PRODUCT", "value": "jeans"},
                    {"type": "COLOR", "value": "blue"},
                    {"type": "SIZE", "value": "32"}
                ],
                description="Add blue jeans to cart"
            ),
            SimulatedCommand(
                command_type=CommandType.CHECKOUT,
                text="proceed to checkout",
                expected_intent=IntentType.CHECKOUT,
                expected_entities=[],
                description="Proceed to checkout"
            )
        ]
        
        return ConversationScenario(
            name="Basic Shopping",
            description="Simple shopping workflow with add items and checkout",
            commands=commands,
            expected_final_cart_items=2
        )
    
    @staticmethod
    def create_complex_shopping_scenario() -> ConversationScenario:
        """Create a complex shopping scenario with modifications"""
        commands = [
            SimulatedCommand(
                command_type=CommandType.SEARCH_PRODUCT,
                text="search for running shoes",
                expected_intent=IntentType.SEARCH,
                expected_entities=[{"type": "PRODUCT", "value": "running shoes"}],
                description="Search for running shoes"
            ),
            SimulatedCommand(
                command_type=CommandType.ADD_ITEM,
                text="add white running shoes size 10",
                expected_intent=IntentType.ADD,
                expected_entities=[
                    {"type": "PRODUCT", "value": "running shoes"},
                    {"type": "COLOR", "value": "white"},
                    {"type": "SIZE", "value": "10"}
                ],
                description="Add white running shoes"
            ),
            SimulatedCommand(
                command_type=CommandType.ADD_ITEM,
                text="add three cotton t-shirts in blue",
                expected_intent=IntentType.ADD,
                expected_entities=[
                    {"type": "PRODUCT", "value": "t-shirts"},
                    {"type": "QUANTITY", "value": "three"},
                    {"type": "MATERIAL", "value": "cotton"},
                    {"type": "COLOR", "value": "blue"}
                ],
                description="Add cotton t-shirts"
            ),
            SimulatedCommand(
                command_type=CommandType.REMOVE_ITEM,
                text="remove one blue t-shirt",
                expected_intent=IntentType.REMOVE,
                expected_entities=[
                    {"type": "QUANTITY", "value": "one"},
                    {"type": "COLOR", "value": "blue"},
                    {"type": "PRODUCT", "value": "t-shirt"}
                ],
                description="Remove one t-shirt"
            ),
            SimulatedCommand(
                command_type=CommandType.VIEW_CART,
                text="what's in my cart now",
                expected_intent=IntentType.SEARCH,
                expected_entities=[],
                description="Check cart after modifications"
            ),
            SimulatedCommand(
                command_type=CommandType.CHECKOUT,
                text="I'm ready to checkout",
                expected_intent=IntentType.CHECKOUT,
                expected_entities=[],
                description="Final checkout"
            )
        ]
        
        return ConversationScenario(
            name="Complex Shopping",
            description="Shopping with search, add, remove, and checkout operations",
            commands=commands,
            expected_final_cart_items=2
        )
    
    @staticmethod
    def create_error_handling_scenario() -> ConversationScenario:
        """Create scenario to test error handling"""
        commands = [
            SimulatedCommand(
                command_type=CommandType.ADD_ITEM,
                text="add nonexistent product to cart",
                expected_intent=IntentType.ADD,
                expected_entities=[{"type": "PRODUCT", "value": "nonexistent product"}],
                expected_success=False,
                description="Try to add non-existent product"
            ),
            SimulatedCommand(
                command_type=CommandType.REMOVE_ITEM,
                text="remove item from empty cart",
                expected_intent=IntentType.REMOVE,
                expected_entities=[{"type": "PRODUCT", "value": "item"}],
                expected_success=False,
                description="Try to remove from empty cart"
            ),
            SimulatedCommand(
                command_type=CommandType.CHECKOUT,
                text="checkout empty cart",
                expected_intent=IntentType.CHECKOUT,
                expected_entities=[],
                expected_success=False,
                description="Try to checkout empty cart"
            )
        ]
        
        return ConversationScenario(
            name="Error Handling",
            description="Test error handling for invalid operations",
            commands=commands,
            expected_final_cart_items=0
        )


def create_test_scenarios() -> List[ConversationScenario]:
    """Create a comprehensive set of test scenarios"""
    return [
        ScenarioBuilder.create_basic_shopping_scenario(),
        ScenarioBuilder.create_complex_shopping_scenario(),
        ScenarioBuilder.create_error_handling_scenario()
    ]