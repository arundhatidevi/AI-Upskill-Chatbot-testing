# Selectors Customization Guide

The chatbot UI automation framework uses CSS selectors to locate and interact with chat elements. These selectors are configurable via environment variables.

## Default Selectors

The following selectors are defined in `.env.example`:

```bash
SELECTOR_OPEN_WIDGET=[data-testid="chat-open-button"]
SELECTOR_INPUT_AREA=[data-testid="chat-input"]
SELECTOR_SEND_BUTTON=[data-testid="chat-send"]
SELECTOR_MESSAGES_CONTAINER=[data-testid="chat-messages"]
SELECTOR_MESSAGE_ROW=.chat-message
SELECTOR_MESSAGE_ROLE_ATTR=data-role
SELECTOR_MESSAGE_TEXT=.message-text
```

## Customizing Selectors

### Step 1: Inspect the Chatbot UI

1. Open the chatbot in your browser
2. Right-click on elements (widget, input, messages) and select "Inspect"
3. Note the element's attributes, classes, and data attributes

### Step 2: Update Selectors in `.env`

Based on your inspection, update the selectors in your `.env` file. Here are examples for common patterns:

#### Example 1: Widget with ID
```bash
SELECTOR_OPEN_WIDGET=#chatbot-toggle-btn
```

#### Example 2: Input with Class
```bash
SELECTOR_INPUT_AREA=.chat-input-field
```

#### Example 3: Complex Nested Selector
```bash
SELECTOR_MESSAGES_CONTAINER=.chat-widget .messages-list
SELECTOR_MESSAGE_ROW=.message-item
```

#### Example 4: Using XPath (advanced)
For complex scenarios, you can use XPath by prefixing with `xpath=`:
```bash
SELECTOR_OPEN_WIDGET=xpath=//button[contains(@class, 'chat-open')]
```

### Step 3: Test Your Selectors

Run a single test to verify your selectors work:

```bash
pytest tests/test_semantic_similarity.py::test_semantic_similarity[greeting_hello] -v
```

## Common Selector Patterns

### Chat Widgets

- **Intercom-style**: `.intercom-launcher`, `#intercom-container`
- **Drift**: `.drift-widget-button`, `.drift-conversation`
- **Zendesk**: `.zEWidget-launcher`, `#webWidget`
- **Custom**: Check for `data-testid`, `data-chat-*`, or custom classes

### Message Extraction

Messages typically have:
- **Role attribute**: `data-role`, `data-sender`, `class` (contains "user" or "bot")
- **Text container**: `.message-text`, `.message-content`, `p` inside message

### Tips

1. **Prefer data attributes**: They're more stable than classes
2. **Use specific selectors**: Avoid overly generic selectors like `div` or `.text`
3. **Test in Playwright Inspector**: Run `PWDEBUG=1 pytest` to debug selectors interactively
4. **Handle dynamic content**: Add waits if messages load asynchronously

## Troubleshooting

### Element not found
- Verify the selector in browser DevTools
- Check if element is inside an iframe: `page.frame_locator("iframe").locator("selector")`
- Increase timeout if element loads slowly

### Multiple elements matched
- Make selector more specific: add parent container or unique attribute
- Use `nth(0)` to select first match, or filter by role

### Messages not extracted correctly
- Inspect the role attribute name and values
- Check if text is in a nested element
- Update `SELECTOR_MESSAGE_TEXT` to match the actual structure

## Example: Adapting for a New Chatbot

Let's say you have a chatbot with this HTML structure:

```html
<div id="chat-root">
  <button class="open-chat">Chat with us</button>
  <div class="chat-window">
    <textarea class="user-input"></textarea>
    <button class="send-msg">Send</button>
    <div class="messages">
      <div class="msg" data-from="user">
        <span class="msg-body">Hello</span>
      </div>
      <div class="msg" data-from="bot">
        <span class="msg-body">Hi there!</span>
      </div>
    </div>
  </div>
</div>
```

Your `.env` would be:

```bash
SELECTOR_OPEN_WIDGET=.open-chat
SELECTOR_INPUT_AREA=.user-input
SELECTOR_SEND_BUTTON=.send-msg
SELECTOR_MESSAGES_CONTAINER=.messages
SELECTOR_MESSAGE_ROW=.msg
SELECTOR_MESSAGE_ROLE_ATTR=data-from
SELECTOR_MESSAGE_TEXT=.msg-body
```

Run your tests and adjust as needed!










