# WTF - Natural Language to Shell Commands

WTF is a command-line tool that converts natural language descriptions into shell commands using AI. Just describe what you want to do, and WTF will generate the appropriate shell command.

## Installation

~~Install from PyPI:~~
(not yet available)

for now, you can install from the source code:

```bash
pip install -e .
```

## Configuration

Before using WTF, you'll need to configure at least one AI provider if `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is not set in your environment. WTF supports OpenAI and Anthropic.

Set up your preferred provider's API key:

```bash
wtf-config set-key openai sk-your-api-key-here
wtf-config set-key anthropic sk-ant-your-api-key-here
```

Set your default provider (optional):
```bash
wtf-config set-default openai
```

if you need to see what the config file looks like, you can use the following command:
```bash
wtf --show-config
```

all configuration is stored in `~/.config/wtf/config.yaml`. You can edit this file directly if needed.

## Usage

Basic usage:
```bash
wtf find all PDF files modified in the last 7 days
```

Specify a different provider:
```bash
wtf -p anthropic list all docker containers including stopped ones
```

Use a specific model:
```bash
wtf -m gpt-4 create a tar archive of all jpg files
```

Execute the command directly:
```bash
wtf -e list all empty directories nested in current directory
```

Show debug information:
```bash
wtf -d "find largest files in current directory"
```

Show history:
```bash
wtf --history
```

## Supported Providers and Models

- OpenAI
  - gpt-3.5-turbo 
  - gpt-4
  - gpt-4o (default)

- Anthropic
  - claude-3-sonnet 
  - claude-3-opus
  - claude-3-haiku
  - claude-3-5-sonnet (default)
  - claude-3-5-haiku
  - claude-3-5-opus

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
