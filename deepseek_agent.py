import json
import traceback
from openai import OpenAI

class DeepSeekAgent:
    def __init__(self, api_key, base_url, model_name, extra_body=None):
        """
        Initialize DeepSeek Agent
        
        :param api_key: API Key
        :param base_url: Base URL
        :param model_name: Model Name
        :param extra_body: Extra parameters passed to the API (e.g., for enabling thinking mode)
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
        self.extra_body = extra_body or {}

    def run(self, messages, tools=None, tool_map=None, max_turns=10):
        """
        Run the Agent loop
        
        :param messages: Initial message list
        :param tools: Tool definitions list (JSON Schema)
        :param tool_map: Tool function mapping dictionary {name: function}
        :param max_turns: Maximum number of conversation turns
        """
        print(f"[*] Agent started with model: {self.model_name}")
        
        for i in range(max_turns):
            print(f"\n--- Turn {i+1} ---")
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=tools,
                    extra_body=self.extra_body
                )
            except Exception as e:
                print(f"[!] API Error: {e}")
                traceback.print_exc()
                break

            message = response.choices[0].message
            
            # 1. Handle Reasoning Content
            # Try multiple ways to get reasoning_content to support different SDK versions
            reasoning_content = getattr(message, 'reasoning_content', None)
            
            if reasoning_content:
                print(f"\n[Thinking Process]:\n{reasoning_content}\n")
                
                # Key: Pass reasoning_content back to the server
                # Construct a dictionary containing reasoning_content and add it to messages
                msg_dict = message.model_dump(exclude_none=True)
                msg_dict['reasoning_content'] = reasoning_content
                messages.append(msg_dict)
            else:
                print("\n[Thinking Process]: None (Not found in response)\n")
                messages.append(message)

            # 2. Print Final Content
            if message.content:
                print(f"[Final Content]:\n{message.content}\n")

            # 3. Handle Tool Calls
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    args_str = tool_call.function.arguments
                    print(f"[Tool Call]: {func_name}({args_str})")
                    
                    if tool_map and func_name in tool_map:
                        try:
                            args = json.loads(args_str)
                            result = tool_map[func_name](**args)
                            
                            # Print result preview
                            result_str = str(result)
                            if len(result_str) < 1000:
                                print(f"[Tool Result]:\n{result_str}")
                            else:
                                preview = result_str[:200].replace('\n', ' ') + "..."
                                print(f"[Tool Result]: {preview}")
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result_str
                            })
                        except json.JSONDecodeError:
                            error_msg = f"Error: Failed to decode arguments: {args_str}"
                            print(error_msg)
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": error_msg
                            })
                        except Exception as e:
                            error_msg = f"Error executing tool {func_name}: {str(e)}"
                            print(error_msg)
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": error_msg
                            })
                    else:
                        print(f"[!] Error: Tool {func_name} not found in tool_map")
            else:
                # No tool calls, usually means task completed or user input needed
                print("\n=== Turn Loop Completed (No more tool calls) ===")
                break
