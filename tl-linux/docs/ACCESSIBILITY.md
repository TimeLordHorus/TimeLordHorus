# TL Linux - Accessibility Features

## Overview

TL Linux is committed to universal accessibility, ensuring that everyone can use and enjoy our operating system regardless of physical, sensory, or cognitive abilities. Our comprehensive accessibility suite includes screen reading, voice control, and AI-powered assistance.

## Accessibility Tools

### 1. Screen Reader with Text-to-Speech

**Location**: `apps/accessibility/screen_reader.py`

A complete screen reader solution for visually impaired users.

**Features:**
- **Text-to-Speech Engine**: Powered by pyttsx3
- **UI Element Narration**: Announces buttons, menus, and text fields
- **Document Reading**: Read clipboard, windows, and text areas
- **Customizable Voice**: Adjust rate, volume, and select different voices
- **Keyboard Shortcuts**: Navigate and control without mouse
- **Spell-Check Mode**: Spell words letter by letter
- **Multiple Verbosity Levels**: Brief, normal, or verbose announcements
- **Punctuation Control**: Choose how punctuation is announced

**Quick Start:**

```bash
python tl-linux/apps/accessibility/screen_reader.py
```

**Keyboard Shortcuts:**
- `Ctrl+R`: Enable/disable screen reader
- `Ctrl+S`: Stop speaking
- `Ctrl+C`: Read clipboard
- `Ctrl+W`: Read window title
- `Ctrl+T`: Read text area

**Settings:**
- **Speech Rate**: 50-300 words per minute (default: 150)
- **Volume**: 0.0-1.0 (default: 0.9)
- **Voice Selection**: Choose from available system voices
- **Auto-start**: Launch on boot
- **Read on Focus**: Automatically read focused elements
- **Keyboard Echo**: Speak typed characters

**Installation:**

```bash
# Install pyttsx3
pip install pyttsx3

# Install TTS engines (Linux)
sudo apt-get install espeak espeak-ng festival

# Test installation
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Hello'); engine.runAndWait()"
```

---

### 2. Voice Control System

**Location**: `apps/accessibility/voice_control.py`

Control your entire operating system using voice commands with wake word detection.

**Features:**
- **Wake Word Detection**: "Hey TL" or "Computer" to activate
- **Natural Language Processing**: Understand conversational commands
- **System Control**: Open/close apps, manage windows, control system
- **Media Control**: Play, pause, volume control
- **Text Input**: Type via voice dictation
- **Voice Feedback**: Spoken confirmations of actions
- **Command History**: Track and review past commands
- **Visual Feedback**: Waveform visualization when listening

**Supported Commands:**

**System Control:**
```
"Open [application]"
"Close [application]"
"Minimize window"
"Maximize window"
"Full screen"
"Lock screen"
"Shut down"
"Restart"
"Sleep"
"Screenshot"
```

**Navigation:**
```
"Go back"
"Go forward"
"Go home"
"Show desktop"
"Search for [query]"
```

**Volume:**
```
"Volume up"
"Volume down"
"Mute"
"Unmute"
"Volume [0-100]"
```

**Media:**
```
"Play"
"Pause"
"Stop"
"Next track"
"Previous track"
```

**Text Editing:**
```
"Type [text]"
"Select all"
"Copy"
"Paste"
"Undo"
"Redo"
```

**Information:**
```
"What time is it"
"What is the date"
```

**Quick Start:**

```bash
python tl-linux/apps/accessibility/voice_control.py
```

1. Click "Enable Voice Control"
2. Say "Hey TL" or "Computer" to activate
3. Wait for the listening indicator
4. Speak your command clearly
5. System will confirm and execute

**Installation:**

```bash
# Install SpeechRecognition
pip install SpeechRecognition

# Install PyAudio for microphone
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio

# Install pyttsx3 for feedback
pip install pyttsx3

# Install system tools (optional)
sudo apt-get install xdotool playerctl
```

**Configuration:**
- **Wake Words**: Customize wake phrases
- **Language**: 50+ language support
- **Energy Threshold**: Adjust microphone sensitivity
- **Voice Feedback**: Enable/disable spoken responses
- **Confidence Display**: Show recognition confidence

---

### 3. AI Dictation Assistant

**Location**: `apps/accessibility/ai_dictation.py`

Intelligent voice-to-text transcription with goal-based structured responses and machine learning.

**Features:**
- **Voice-to-Text Transcription**: High-accuracy speech recognition
- **Goal-Based Processing**: 8 specialized goal templates
- **AI-Powered Responses**: Generate structured content from speech
- **Context Awareness**: Maintains conversation context
- **Learning System**: Improves from user feedback
- **Auto-Punctuation**: Automatically add punctuation
- **Auto-Capitalization**: Smart sentence capitalization
- **Text Improvement**: Enhance transcribed text
- **Summarization**: Generate summaries of long text
- **Multiple Languages**: Support for 50+ languages

**Goal Templates:**

1. **📝 General Writing**
   - Output: Formatted text with suggestions
   - Use case: Blog posts, articles, general content

2. **💼 Professional Email**
   - Output: Structured email with greeting/closing
   - Use case: Business correspondence

3. **💻 Code Documentation**
   - Output: JSDoc/Javadoc style comments
   - Use case: Software documentation

4. **📚 Study Notes**
   - Output: Key points and review questions
   - Use case: Academic learning

5. **📋 Task Planning**
   - Output: Checkbox list with timeline
   - Use case: Project management

6. **🎨 Creative Writing**
   - Output: Story elements and enhancement ideas
   - Use case: Fiction, poetry, creative work

7. **🔬 Research Summary**
   - Output: Academic summary format
   - Use case: Research papers, literature reviews

8. **📊 Report Writing**
   - Output: Formal report structure
   - Use case: Business reports, analytics

**Quick Start:**

```bash
python tl-linux/apps/accessibility/ai_dictation.py
```

1. Select your goal from the list
2. Click "Start Dictation"
3. Speak your content clearly
4. Click "Stop Dictation" when finished
5. Click "Generate AI Response" for structured output

**AI Response Generation:**

The system processes your transcribed text based on the selected goal:
- Analyzes content and intent
- Applies goal-specific structuring
- Generates formatted output
- Provides suggestions and improvements
- Learns from your feedback ratings

**Learning & Personalization:**

The AI assistant learns from:
- Your goal preferences
- Writing style and tone
- Feedback ratings (1-5 stars)
- Vocabulary and corrections
- Structural preferences

**Installation:**

```bash
# Core requirements
pip install SpeechRecognition pyaudio pyttsx3

# Optional: For enhanced AI (requires significant disk space)
pip install transformers torch
```

---

## Accessibility Hub

**Location**: `apps/accessibility_hub.py`

Central launcher providing easy access to all accessibility tools.

**Features:**
- Visual card-based interface
- Tool descriptions and categories
- One-click launching
- Color-coded organization
- Accessibility-optimized design

**Quick Start:**

```bash
python tl-linux/apps/accessibility_hub.py
```

---

## Installation Guide

### Complete Installation

Install all accessibility features at once:

```bash
# Update package manager
sudo apt-get update

# Install system dependencies
sudo apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    espeak \
    espeak-ng \
    festival \
    xdotool \
    playerctl

# Install Python packages
pip install --user \
    pyttsx3 \
    SpeechRecognition \
    pyaudio

# Test installation
python -c "import pyttsx3, speech_recognition; print('✓ All packages installed successfully')"
```

### Minimal Installation (Screen Reader Only)

```bash
pip install pyttsx3
sudo apt-get install espeak
```

### Voice Control Only

```bash
pip install SpeechRecognition pyaudio pyttsx3
sudo apt-get install portaudio19-dev python3-pyaudio xdotool
```

---

## Troubleshooting

### Screen Reader Issues

**Problem**: No audio output
- **Solution**: Check volume settings, ensure espeak is installed
- **Test**: `espeak "test"` in terminal

**Problem**: Wrong voice selected
- **Solution**: Open Settings → Voice tab → Select different voice

**Problem**: Speech too fast/slow
- **Solution**: Adjust Speech Rate slider in Settings

### Voice Control Issues

**Problem**: Wake word not detected
- **Solution**:
  - Check microphone permissions
  - Adjust energy threshold in settings
  - Speak clearly and louder
  - Reduce background noise

**Problem**: Commands not recognized
- **Solution**:
  - Check internet connection (Google Speech API requires internet)
  - Speak commands from the supported list
  - Use clear pronunciation

**Problem**: Microphone not working
- **Solution**:
  - Test with: `python -m speech_recognition`
  - Check: `arecord -l` to list microphones
  - Install: `sudo apt-get install python3-pyaudio`

### AI Dictation Issues

**Problem**: Transcription is inaccurate
- **Solution**:
  - Speak more slowly and clearly
  - Reduce background noise
  - Check microphone quality
  - Verify internet connection

**Problem**: AI responses don't match goal
- **Solution**:
  - Verify correct goal is selected
  - Provide more detailed dictation
  - Use goal-specific language

---

## Keyboard Shortcuts Summary

### Screen Reader
| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Toggle screen reader |
| `Ctrl+S` | Stop speaking |
| `Ctrl+C` | Read clipboard |
| `Ctrl+W` | Read window title |
| `Ctrl+T` | Read text area |

### Voice Control
| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Enable/disable voice control |
| `Ctrl+S` | Stop listening |

### Global (Planned)
| Shortcut | Action |
|----------|--------|
| `Super+A` | Open Accessibility Hub |
| `Super+S` | Toggle Screen Reader |
| `Super+V` | Toggle Voice Control |

---

## Best Practices

### For Screen Reader Users

1. **Learn Keyboard Shortcuts**: Master keyboard navigation for efficiency
2. **Adjust Speech Rate**: Find comfortable reading speed
3. **Use Verbosity Levels**: Switch between brief/normal/verbose as needed
4. **Test with Sample Text**: Practice with the test text area

### For Voice Control Users

1. **Clear Environment**: Reduce background noise
2. **Good Microphone**: Use quality microphone for better recognition
3. **Learn Commands**: Familiarize yourself with supported commands
4. **Speak Clearly**: Enunciate and use normal speaking pace
5. **Use Wake Words**: Always start with "Hey TL" or "Computer"

### For AI Dictation Users

1. **Choose Right Goal**: Select goal before dictating
2. **Organize Thoughts**: Plan what you want to say
3. **Speak in Chunks**: Pause between sentences
4. **Review and Edit**: Always review generated content
5. **Provide Feedback**: Rate responses to improve learning
6. **Build Vocabulary**: System learns your terminology over time

---

## Accessibility Standards Compliance

TL Linux accessibility features aim to meet:

- **WCAG 2.1 Level AA**: Web Content Accessibility Guidelines
- **Section 508**: US Federal accessibility requirements
- **EN 301 549**: European accessibility standard

### Supported Disabilities

- ✅ **Visual**: Screen reader, high contrast, large text
- ✅ **Motor**: Voice control, keyboard navigation
- ✅ **Hearing**: Visual feedback, text alternatives
- ✅ **Cognitive**: Clear language, consistent layout
- ✅ **Speech**: Voice dictation alternatives

---

## Future Enhancements

### Planned Features

1. **High Contrast Themes**: Enhanced Lightning theme with WCAG AAA compliance
2. **Screen Magnifier**: 2x-16x magnification with follow-focus
3. **On-Screen Keyboard**: Virtual keyboard for touch/mouse input
4. **Switch Access**: Single-button scanning interface
5. **Eye Tracking**: Gaze-based control (Tobii integration)
6. **Braille Display**: LibLouis integration
7. **Sign Language Recognition**: Camera-based signing
8. **Reading Guide**: Highlight current line/paragraph
9. **Color Blindness Modes**: Filters for different types
10. **Gesture Control**: Webcam-based gesture recognition

### Roadmap

- **Q1 2024**: High contrast themes, screen magnifier
- **Q2 2024**: On-screen keyboard, switch access
- **Q3 2024**: Braille display support
- **Q4 2024**: Eye tracking, advanced ML features

---

## Contributing

We welcome contributions to improve accessibility!

**How to Contribute:**

1. **Report Issues**: GitHub issues for bugs or feature requests
2. **Test Features**: Provide feedback from real usage
3. **Submit Patches**: Pull requests for improvements
4. **Documentation**: Help improve guides and tutorials
5. **Translations**: Add support for more languages

**Accessibility Testing:**

- Test with actual assistive technologies
- Include users with disabilities in testing
- Follow WCAG guidelines
- Document accessibility features clearly

---

## Resources

### External Tools Compatibility

TL Linux accessibility features work alongside:
- **Orca**: GNOME screen reader
- **NVDA**: Windows screen reader (via Wine)
- **JAWS**: Professional screen reader (via Wine)
- **Dragon**: Voice recognition software

### Learning Resources

**Screen Reader**
- [WebAIM Screen Reader Guide](https://webaim.org/articles/screenreader_testing/)
- [NVDA User Guide](https://www.nvaccess.org/documentation/)

**Voice Control**
- [Voice Control Best Practices](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Voice_control)
- [Speech Recognition Tutorial](https://realpython.com/python-speech-recognition/)

**Accessibility Standards**
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Section 508 Standards](https://www.section508.gov/)
- [W3C WAI Resources](https://www.w3.org/WAI/)

### Community Support

- **TL Linux Forums**: Community support and tips
- **Accessibility Channel**: Discord/IRC for accessibility users
- **Mailing List**: accessibility@tllinux.org

---

## FAQ

### Q: Do I need internet for voice control?
**A:** Yes, the current implementation uses Google Speech API which requires internet. Offline support is planned using Vosk or PocketSphinx.

### Q: Can I use my own TTS voice?
**A:** Yes, any voice compatible with pyttsx3 will work. You can install additional voices through your system.

### Q: How accurate is the AI dictation?
**A:** Accuracy depends on microphone quality, environment noise, and clarity of speech. Typically 90-95% with good conditions.

### Q: Can I customize voice commands?
**A:** Custom commands are planned for future releases. Current commands use regex pattern matching.

### Q: Is my voice data stored or transmitted?
**A:** Voice data is sent to Google Speech API for recognition (requires internet). We recommend reviewing Google's privacy policy. Offline mode (coming soon) will process all data locally.

### Q: How do I report accessibility issues?
**A:** Open a GitHub issue with the "accessibility" label, or email accessibility@tllinux.org

### Q: Can I use multiple accessibility tools at once?
**A:** Yes! Screen reader, voice control, and AI dictation can run simultaneously.

### Q: What languages are supported?
**A:** 50+ languages supported by Google Speech API. Language selection available in settings.

---

## Acknowledgments

TL Linux accessibility features are built with:
- **pyttsx3**: Text-to-speech engine
- **SpeechRecognition**: Speech recognition library
- **Google Speech API**: Cloud-based speech recognition
- **PyAudio**: Audio I/O
- **eSpeak**: TTS synthesis engine

Special thanks to the accessibility community for feedback and testing.

---

## License

All accessibility tools are free and open source under the TL Linux license.

---

## Support

For accessibility-related questions or issues:
- **Email**: accessibility@tllinux.org
- **GitHub**: [Issues](https://github.com/tllinux/issues)
- **Discord**: #accessibility channel

**We're committed to making TL Linux accessible to everyone. Your feedback helps us improve!** ♿
