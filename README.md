# MCP Client

This project is an implementation of an MCP (Model Context Protocol) client for OpenAI Agents SDK.

## Features

- Supports agent orchestration, allowing multiple agents to collaborate and delegate tasks.
- Flexible configuration: Add or modify MCP servers dynamically through the configuration file.
- Easy integration with OpenAI Agents SDK.
- Scalable design to handle complex workflows with multiple agents.
- Customizable agent instructions and behavior.

## Requirements

- Python 3.8 or higher
- OpenAI Agents SDK (`pip install openai-agents`)

## Usage

Make configuration file (`config.json`)

```json
{
  "agents": [
    {
      "name": "agent1",
      "model": "model_name",
      "instructions": "Agent 1 instructions",
      "cache_tools_list": true,
      "assistants": ["agent2"],
      "mcp_servers": [
        {
          "command": "path/to/command",
          "args": ["--arg1", "value1"]
        }
      ]
    },
    {
      "name": "agent2",
      "model": "model_name",
      "instructions": "Agent 2 instructions",
      "cache_tools_list": false,
      "assistants": [],
      "mcp_servers": [
        {
          "command": "path/to/command",
          "args": ["--arg2", "value2"]
        }
      ]
    }
  ],
  "starting_agent": "agent1"
}
```

Explanation of Fields
- agents: A list of agent configurations.
  - name: The unique name of the agent.
  - model: The model associated with the agent.
  - instructions: Instructions or description for the agent.
  - cache_tools_list: A boolean indicating whether to cache the tools list.
  - assistants: A list of other agents that this agent can hand off tasks to.
  - mcp_servers: A list of MCP server configurations.
    - command: The command to start the MCP server.
    - args: A list of arguments for the command.
- starting_agent: The name of the agent to start the workflow.

**Notes**
- Ensure that all agents listed in the assistants field exist in the agents list.
- **Warning:** Circular dependencies between agents may lead to infinite loops during execution. Ensure that the configuration avoids such scenarios.

Run the client with:
```bash
export OPENAI_API_KEY=<Your API KEY>
python main.py <config_file>
```

Use exit, quit, or q to terminate the program during execution.
