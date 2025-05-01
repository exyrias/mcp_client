import asyncio
from agents import Agent, Runner, gen_trace_id, trace, ItemHelpers
from agents.mcp import MCPServerStdio
# from agents.extensions.visualization import draw_graph
from contextlib import AsyncExitStack
import json
import readline # for accepting Japanese input
import sys


def parse_config(config_file: str) -> dict:
  with open(config_file, 'r') as file:
    config = file.read()
  return json.loads(config)


async def main():
  if len(sys.argv) < 2:
    print(f'Usage: python {sys.argv[0]} <config_file>')
    sys.exit(1)
  config = parse_config(sys.argv[1])

  # Create MCP servers
  async with AsyncExitStack() as stack:
    agents = dict()
    agents_candidates = {ag['name']: ag for ag in config['agents']}
    # check if all assistants are available
    for agent_name, ag in agents_candidates.items():
      if not set(ag['assistants']).issubset(agents_candidates.keys()):
        print(f"Error: Agent '{agent_name}' has invalid assistants.")
        sys.exit(1)
    # TODO: Currently, circular dependencies are not checked.

    # initialize agents
    while len(agents_candidates) > len(agents):
      for agent_name, ag in agents_candidates.items():
        if agent_name not in agents.keys() and set(ag['assistants']).issubset(agents.keys()):
          mcp_servers = [
            await stack.enter_async_context(
              MCPServerStdio(
                name=agent_name,
                params={
                  'command': server['command'],
                  'args': server['args']
                },
                cache_tools_list=server['cache_tools_list'],
              )
            )
            for server in ag['mcp_servers']
          ]
          agents[agent_name] = Agent(
            model=ag['model'],
            name=agent_name,
            instructions=ag['instructions'],
            mcp_servers=mcp_servers,
            # tools=[WebSearchTool()],
            handoffs=[agents[assistant_name] for assistant_name in ag['assistants']],
          )

    starting_agent = agents[config['starting_agent']]
    print(f'Starting agent: {starting_agent.name}')

    # draw_graph(starting_agent).view()

    trace_id = gen_trace_id()
    print(f'Trace ID: {trace_id}')
    with trace(workflow_name='MCP test', trace_id=trace_id):
      result = None

      while True:
        try:
          # Run the agent with a query
          print()
          print("Enter your query (or 'exit' to quit):")
          text = input('>>> ')
          if text == '':
            continue
          elif text.lower() in ['exit', 'quit', 'q']:
            break

          print(f'Query: {text}')
          print()

          if result is None:
            new_input = text
          else:
            new_input = result.to_input_list() + [
              {
                'role': 'user',
                'content': text,
              }
            ]
          # for not streaming run
          # result = await Runner.run(starting_agent, new_input)
          # print(result.final_output)

          # for streaming run
          result = Runner.run_streamed(starting_agent, new_input)
          async for event in result.stream_events():
            # We'll ignore the raw responses event deltas
            if event.type == 'raw_response_event':
              continue
            # When the agent updates, print that
            elif event.type == 'agent_updated_stream_event':
              print(f'Agent updated: {event.new_agent.name}')
              continue
            # When items are generated, print them
            elif event.type == 'run_item_stream_event':
              if event.item.type == 'tool_call_item':
                print(f'-- Tool was called: {event.item.to_input_item()}')
              elif event.item.type == 'tool_call_output_item':
                print(f'-- Tool output: {event.item.output}')
              elif event.item.type == 'message_output_item':
                print(f'-- Message output:\n {ItemHelpers.text_message_output(event.item)}')
              else:
                pass  # Ignore other event types

        except KeyboardInterrupt:
          print('Stopped')
          break
        except Exception as e:
          print(f'Error occurred:\n{e}')
          print('Please try again.')


if __name__ == '__main__':
  asyncio.run(main())

