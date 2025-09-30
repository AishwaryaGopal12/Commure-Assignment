"""
LangGraph agent implementation for SQL query generation.

This module defines the Agent class that orchestrates LLM calls and tool
executions using a graph-based workflow pattern.
"""
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

class AgentState(TypedDict):
    """
    Type definition for the agent's state in the LangGraph workflow.

    Attributes:
        messages (Annotated[list[AnyMessage], operator.add]): List of messages that
            represents the conversation history. The operator.add annotation means
            new messages are appended to existing ones rather than replacing them.
    """
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:
    """
    LangGraph-based agent that orchestrates LLM calls and tool executions.

    This agent implements a graph-based workflow where the LLM can decide to either
    finish responding or call tools to gather additional information. The workflow
    continues in a loop until the LLM decides no more tool calls are needed.

    Workflow:
        1. Start at "llm" node - calls the language model
        2. Check if LLM requested tool calls
        3. If yes, go to "action" node - executes tools and returns to "llm"
        4. If no, end the workflow and return final response

    Attributes:
        system (str): System prompt that provides context and instructions to the LLM.
        graph (CompiledGraph): The compiled LangGraph state machine.
        tools (dict): Dictionary mapping tool names to tool functions.
        model: The LLM with tools bound to it for function calling.
    """
    def __init__(self, model, tools, system=""):
        """
        Initialize the agent with model, tools, and optional system prompt.

        Sets up the LangGraph workflow by defining nodes (llm, action), edges between
        them, and conditional routing logic based on whether tools are called.

        Args:
            model: Language model instance (e.g., ChatOpenAI) that supports tool binding.
            tools (list): List of tool functions/objects that the LLM can call.
            system (str, optional): System prompt providing context to the LLM. Defaults to "".

        Note:
            The graph is compiled immediately upon initialization and stored in self.graph.
        """
        # Store the system prompt for use in call_openai
        self.system = system

        # Initialize the state graph with AgentState type definition
        graph = StateGraph(AgentState)
        # Add the LLM node - this is where the language model processes messages
        graph.add_node("llm", self.call_openai)

        # Add the action node - this is where tools are executed
        graph.add_node("action", self.take_action)

        # Add conditional edges from llm node:
        # - If exists_action returns True, route to "action" node
        # - If exists_action returns False, route to END (finish workflow)
        graph.add_conditional_edges("llm", self.exists_action, {True: "action", False: END})

        # Add unconditional edge from action back to llm
        # After tools execute, always return to the LLM to process results
        graph.add_edge("action", "llm")

        # Set "llm" as the entry point - workflow always starts here
        graph.set_entry_point("llm")

        # Compile the graph into an executable workflow
        self.graph = graph.compile()

        # Create a dictionary mapping tool names to tool objects for quick lookup
        self.tools = {tool.name: tool for tool in tools}

        # Bind the tools to the model so it knows what functions it can call
        self.model = model.bind_tools(tools)

    def call_openai(self, state: AgentState):
        """
        Node function that invokes the language model with current conversation state.

        This is the main "thinking" node where the LLM processes the conversation
        history, potentially decides to call tools, or provides a final answer.

        Args:
            state (AgentState): Current state containing message history.

        Returns:
            dict: Updated state with new message from the LLM appended.
                 Format: {'messages': [new_message]}

        Note:
            If a system prompt was provided during initialization, it's prepended
            to the messages before sending to the LLM.
        """
        # Extract the message history from the current state
        messages = state['messages']

        # If a system prompt exists, prepend it to provide context to the LLM
        # This ensures the LLM always has its instructions available
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages

        # Invoke the language model with the full message history
        # The model may return a regular response or include tool_calls
        message = self.model.invoke(messages)

        # Return the new message wrapped in a dict
        # The operator.add annotation ensures it gets appended to existing messages
        return {'messages': [message]}

    def exists_action(self, state: AgentState):
        """
        Conditional edge function that determines if tool calls are needed.

        This function checks the most recent message from the LLM to see if it
        contains any tool_calls. If yes, workflow routes to the action node.
        If no, workflow ends and returns the final response.

        Args:
            state (AgentState): Current state containing message history.

        Returns:
            bool: True if the LLM requested tool calls, False otherwise.

        Note:
            This acts as the "routing decision" in the workflow graph.
        """
        # Get the most recent message (last one in the list)
        result = state['messages'][-1]

        # Check if the message has any tool_calls
        # If tool_calls list has length > 0, return True to trigger action node
        return len(result.tool_calls) > 0

    def take_action(self, state: AgentState):
        """
        Node function that executes all tool calls requested by the LLM.

        When the LLM decides it needs additional information, it includes tool_calls
        in its response. This function executes each of those tool calls and returns
        the results as ToolMessages that get added back to the conversation history.

        Args:
            state (AgentState): Current state containing message history with tool calls.

        Returns:
            dict: Updated state with ToolMessage results for each tool call.
                 Format: {'messages': [ToolMessage1, ToolMessage2, ...]}

        Note:
            After this node completes, the workflow always returns to the "llm" node
            so the LLM can process the tool results and decide next steps.
        """
        # Extract tool calls from the most recent LLM message
        tool_calls = state['messages'][-1].tool_calls

        # Initialize list to collect results from all tool executions
        results = []

        # Execute each tool call sequentially
        for t in tool_calls:
            # Look up the tool function by name from the tools dictionary
            # Invoke the tool with the arguments provided by the LLM
            result = self.tools[t['name']].invoke(t['args'])

            # Wrap the result in a ToolMessage with metadata
            # tool_call_id: Links this result back to the specific tool call
            # name: The name of the tool that was executed
            # content: The actual result from the tool (converted to string)
            results.append(ToolMessage(
                tool_call_id=t['id'],
                name=t['name'],
                content=str(result)
            ))

        # Return all tool results wrapped in a dict
        # These messages will be appended to the conversation history
        # and the workflow will loop back to the LLM to process them
        return {'messages': results}