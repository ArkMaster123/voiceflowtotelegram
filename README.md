# 🤖 VoiceFlow Telegram Bot

The missing link between Voiceflow and Telegram! This project eliminates the complexity of setting up Telegram webhooks and provides a robust integration layer that just works.

## 🎯 Why This Project?

### Solving Key Pain Points
- **No Webhook Hassle**: Handles all the complex Telegram webhook setup for you
- **Ready to Deploy**: Works out of the box with minimal configuration
- **Production Ready**: Built-in error handling, logging, and conversation management

## ✨ Features

### 💬 Messaging Integration
- Seamless natural language conversations
- Automatic message handling and routing
- Built-in conversation state management
- Comprehensive error handling and recovery

### 🎨 Rich Media Support
- Interactive buttons and menus
- Image and media sharing
- Dynamic carousels
- Custom keyboard layouts

### 🎨 Interactive Elements
- **Text Messages**: Natural language processing for fluid conversations
- **Buttons**: Interactive inline buttons for user choices
- **Image Cards**: Rich media cards with images and text
- **Carousels**: Swipeable carousel messages with multiple items

## 🎬 Examples

### Button Example
```python
# In Voiceflow, create a choice step with options:
- "Show me products" 
- "Contact support"
- "Track order"

# The bot will display these as clickable buttons!
```

### Image Card Example
```python
# In Voiceflow, use a visual step:
{
    "image": "https://example.com/product.jpg",
    "title": "New Product",
    "description": "Check out our latest release!",
    "buttons": ["Buy Now", "Learn More"]
}
```

### Carousel Example
```python
# Create a carousel in Voiceflow:
[
    {
        "image": "product1.jpg",
        "title": "Item 1",
        "description": "First item"
    },
    {
        "image": "product2.jpg",
        "title": "Item 2",
        "description": "Second item"
    }
]
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from @BotFather)
- Voiceflow API Key
- Voiceflow Project ID

### 🐳 Docker Installation
1. Clone and enter:
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your tokens
```

3. Launch with Docker:
```bash
docker build -t telegram-voiceflow-bot .
docker run -d --env-file .env telegram-voiceflow-bot
```

### 🛠 Manual Setup
1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Configure environment variables
3. Launch:
```bash
python main.py
```

## 🔧 Development

### Integration Details
- Uses `python-telegram-bot` for Telegram API
- Voiceflow Runtime API for conversation management
- Comprehensive logging (file + console)

### Customization
- Modify `main.py` for custom message handling
- Add new interactive features
- Extend error handling

## 📝 License
MIT License - Feel free to use and modify!

## 🤝 Contributing
Contributions welcome! Please read our contributing guidelines.

## 🌟 Show Your Support
If you find this project useful, give it a star! ⭐️
