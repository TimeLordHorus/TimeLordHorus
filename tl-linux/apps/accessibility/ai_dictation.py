#!/usr/bin/env python3
"""
TL Linux - AI-Powered Dictation Assistant
Intelligent voice-to-text with goal-based structured responses
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from pathlib import Path
import threading
import time
from datetime import datetime
import re

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

class AI_DictationAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 TL AI Dictation Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')

        self.config_file = Path.home() / '.config' / 'tl-linux' / 'ai_dictation.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config = self.load_config()

        # Speech recognition
        self.recognizer = sr.Recognizer() if HAS_SR else None
        self.microphone = None
        self.tts_engine = None

        # AI/Learning model state
        self.user_goals = {}
        self.conversation_context = []
        self.current_goal = None
        self.learning_data = self.load_learning_data()

        # Dictation state
        self.is_recording = False
        self.transcribed_text = ""
        self.session_history = []

        self.initialize_engines()
        self.setup_ui()

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'language': 'en-US',
            'auto_punctuation': True,
            'auto_capitalize': True,
            'voice_feedback': True,
            'goal_detection': True,
            'context_awareness': True,
            'learning_enabled': True
        }

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_learning_data(self):
        """Load learning/training data"""
        learning_file = Path.home() / '.config' / 'tl-linux' / 'dictation_learning.json'

        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        return {
            'user_preferences': {},
            'goal_patterns': {},
            'corrections': {},
            'vocabulary': [],
            'writing_style': {
                'formality': 'neutral',
                'tone': 'professional',
                'length_preference': 'medium'
            }
        }

    def save_learning_data(self):
        """Save learning data"""
        learning_file = Path.home() / '.config' / 'tl-linux' / 'dictation_learning.json'

        try:
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            print(f"Error saving learning data: {e}")

    def initialize_engines(self):
        """Initialize speech recognition and TTS"""
        if HAS_SR:
            try:
                self.microphone = sr.Microphone()

                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                self.recognizer.energy_threshold = 4000
                self.recognizer.dynamic_energy_threshold = True

            except Exception as e:
                print(f"Error initializing microphone: {e}")

        if HAS_TTS:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 165)
                self.tts_engine.setProperty('volume', 0.85)
            except Exception as e:
                print(f"Error initializing TTS: {e}")

    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', pady=15)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="🤖 AI Dictation Assistant",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack()

        tk.Label(
            header,
            text="Intelligent voice-to-text with goal-based structured responses",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack()

        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Controls & Goal Selection
        left_panel = tk.Frame(main_container, bg='#2c3e50', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Goal selection
        goal_frame = tk.Frame(left_panel, bg='#2c3e50', pady=15)
        goal_frame.pack(fill=tk.X)

        tk.Label(
            goal_frame,
            text="Select Your Goal:",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=(0, 10))

        self.goal_var = tk.StringVar(value='writing')

        goals = [
            ('📝 General Writing', 'writing'),
            ('💼 Professional Email', 'email'),
            ('💻 Code Documentation', 'code_doc'),
            ('📚 Study Notes', 'notes'),
            ('📋 Task Planning', 'planning'),
            ('🎨 Creative Writing', 'creative'),
            ('🔬 Research Summary', 'research'),
            ('📊 Report Writing', 'report')
        ]

        for text, value in goals:
            tk.Radiobutton(
                goal_frame,
                text=text,
                variable=self.goal_var,
                value=value,
                bg='#2c3e50',
                fg='white',
                selectcolor='#34495e',
                font=('Arial', 10),
                command=self.on_goal_change
            ).pack(anchor='w', padx=20, pady=2)

        # Recording control
        control_frame = tk.Frame(left_panel, bg='#34495e', pady=20)
        control_frame.pack(fill=tk.X, pady=20)

        self.record_btn = tk.Button(
            control_frame,
            text="🎤 Start Dictation",
            command=self.toggle_recording,
            bg='#27ae60',
            fg='white',
            font=('Arial', 14, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=15
        )
        self.record_btn.pack()

        self.status_label = tk.Label(
            control_frame,
            text="Ready to dictate",
            font=('Arial', 10),
            bg='#34495e',
            fg='#95a5a6'
        )
        self.status_label.pack(pady=(10, 0))

        # Quick actions
        actions_frame = tk.Frame(left_panel, bg='#2c3e50', pady=10)
        actions_frame.pack(fill=tk.X)

        tk.Label(
            actions_frame,
            text="Quick Actions:",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=(0, 10))

        tk.Button(
            actions_frame,
            text="🤖 Generate AI Response",
            command=self.generate_ai_response,
            bg='#9b59b6',
            fg='white',
            relief=tk.FLAT,
            padx=10,
            pady=8
        ).pack(fill=tk.X, padx=15, pady=3)

        tk.Button(
            actions_frame,
            text="✨ Improve Text",
            command=self.improve_text,
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=10,
            pady=8
        ).pack(fill=tk.X, padx=15, pady=3)

        tk.Button(
            actions_frame,
            text="📋 Summarize",
            command=self.summarize_text,
            bg='#16a085',
            fg='white',
            relief=tk.FLAT,
            padx=10,
            pady=8
        ).pack(fill=tk.X, padx=15, pady=3)

        tk.Button(
            actions_frame,
            text="🗑️ Clear All",
            command=self.clear_all,
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=10,
            pady=8
        ).pack(fill=tk.X, padx=15, pady=3)

        # Right panel - Text areas
        right_panel = tk.Frame(main_container, bg='#1e1e1e')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Notebook for different views
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Transcription tab
        transcription_frame = tk.Frame(notebook, bg='white')
        notebook.add(transcription_frame, text="📝 Transcription")

        tk.Label(
            transcription_frame,
            text="Transcribed Text:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))

        self.transcription_text = scrolledtext.ScrolledText(
            transcription_frame,
            font=('Arial', 12),
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.transcription_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # AI Response tab
        response_frame = tk.Frame(notebook, bg='white')
        notebook.add(response_frame, text="🤖 AI Response")

        tk.Label(
            response_frame,
            text="Goal-Based Structured Response:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))

        self.response_text = scrolledtext.ScrolledText(
            response_frame,
            font=('Arial', 12),
            wrap=tk.WORD,
            padx=10,
            pady=10,
            bg='#f0f8ff'
        )
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Feedback frame
        feedback_frame = tk.Frame(response_frame, bg='white', pady=10)
        feedback_frame.pack(fill=tk.X, padx=10)

        tk.Label(
            feedback_frame,
            text="Rate this response:",
            font=('Arial', 10),
            bg='white'
        ).pack(side=tk.LEFT, padx=5)

        for i in range(1, 6):
            tk.Button(
                feedback_frame,
                text="⭐" * i,
                command=lambda rating=i: self.rate_response(rating),
                bg='#ecf0f1',
                relief=tk.FLAT,
                padx=5
            ).pack(side=tk.LEFT, padx=2)

        # Context tab
        context_frame = tk.Frame(notebook, bg='white')
        notebook.add(context_frame, text="💡 Context & Learning")

        tk.Label(
            context_frame,
            text="Conversation Context:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))

        self.context_text = scrolledtext.ScrolledText(
            context_frame,
            font=('Arial', 10),
            wrap=tk.WORD,
            padx=10,
            pady=10,
            height=10
        )
        self.context_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Learning insights
        tk.Label(
            context_frame,
            text="Learning Insights:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))

        self.insights_text = scrolledtext.ScrolledText(
            context_frame,
            font=('Arial', 10),
            wrap=tk.WORD,
            padx=10,
            pady=10,
            height=8,
            bg='#fffef0'
        )
        self.insights_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.update_insights()

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready" + ("" if HAS_SR else " - Warning: speech_recognition not installed"),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#2c3e50',
            fg='white',
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        if not HAS_SR:
            self.show_installation_guide()

    def on_goal_change(self):
        """Handle goal selection change"""
        self.current_goal = self.goal_var.get()
        self.status_bar.config(text=f"Goal set to: {self.current_goal}")

        # Update context
        self.conversation_context.append({
            'type': 'goal_change',
            'goal': self.current_goal,
            'timestamp': time.time()
        })

        if self.config.get('voice_feedback'):
            goal_names = {
                'writing': 'general writing',
                'email': 'professional email',
                'code_doc': 'code documentation',
                'notes': 'study notes',
                'planning': 'task planning',
                'creative': 'creative writing',
                'research': 'research summary',
                'report': 'report writing'
            }
            self.speak(f"Goal set to {goal_names.get(self.current_goal, self.current_goal)}")

    def toggle_recording(self):
        """Toggle voice recording"""
        if not HAS_SR:
            messagebox.showerror(
                "Speech Recognition Not Available",
                "speech_recognition library is required.\n\n"
                "Install with: pip install SpeechRecognition pyaudio"
            )
            return

        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """Start recording voice"""
        self.is_recording = True
        self.record_btn.config(text="⏹️ Stop Dictation", bg='#e74c3c')
        self.status_label.config(text="🎤 Listening...", fg='#27ae60')

        if self.config.get('voice_feedback'):
            self.speak("Listening")

        # Start listening thread
        threading.Thread(target=self.record_voice, daemon=True).start()

    def stop_recording(self):
        """Stop recording voice"""
        self.is_recording = False
        self.record_btn.config(text="🎤 Start Dictation", bg='#27ae60')
        self.status_label.config(text="Processing...", fg='#95a5a6')

    def record_voice(self):
        """Record and transcribe voice"""
        if not self.microphone or not self.recognizer:
            return

        try:
            with self.microphone as source:
                # Listen for speech
                audio = self.recognizer.listen(source, timeout=30, phrase_time_limit=30)

            self.root.after(0, lambda: self.status_label.config(text="Transcribing..."))

            # Recognize speech
            text = self.recognizer.recognize_google(audio, language=self.config.get('language', 'en-US'))

            # Process text
            if self.config.get('auto_capitalize'):
                text = text.capitalize()

            if self.config.get('auto_punctuation'):
                text = self.add_punctuation(text)

            # Update UI
            self.root.after(0, lambda: self.append_transcription(text))
            self.root.after(0, lambda: self.status_label.config(text="Ready to dictate", fg='#95a5a6'))

            # Add to context
            self.conversation_context.append({
                'type': 'transcription',
                'text': text,
                'goal': self.current_goal,
                'timestamp': time.time()
            })

            # Update context display
            self.root.after(0, self.update_context_display)

            # If still recording, continue
            if self.is_recording:
                self.root.after(100, self.record_voice)

        except sr.WaitTimeoutError:
            self.root.after(0, lambda: self.status_label.config(text="No speech detected", fg='#e74c3c'))
            if self.is_recording:
                self.root.after(1000, self.record_voice)

        except sr.UnknownValueError:
            self.root.after(0, lambda: self.status_label.config(text="Could not understand", fg='#e74c3c'))
            if self.is_recording:
                self.root.after(1000, self.record_voice)

        except Exception as e:
            print(f"Recording error: {e}")
            self.root.after(0, lambda: self.stop_recording())

    def add_punctuation(self, text):
        """Add basic auto-punctuation"""
        # This is a simplified version - real implementation would use ML
        text = text.strip()

        # Add period at end if missing
        if text and text[-1] not in '.!?':
            text += '.'

        return text

    def append_transcription(self, text):
        """Append text to transcription"""
        current = self.transcription_text.get('1.0', 'end-1c')

        if current:
            self.transcription_text.insert('end', ' ')

        self.transcription_text.insert('end', text)
        self.transcription_text.see('end')

        self.transcribed_text = self.transcription_text.get('1.0', 'end-1c')

    def generate_ai_response(self):
        """Generate goal-based AI response"""
        text = self.transcribed_text

        if not text.strip():
            messagebox.showwarning("No Text", "Please dictate some text first")
            return

        self.status_bar.config(text="Generating AI response...")

        # Get goal
        goal = self.goal_var.get()

        # Generate response based on goal
        response = self.process_with_goal(text, goal)

        # Display response
        self.response_text.delete('1.0', 'end')
        self.response_text.insert('1.0', response)

        # Add to context
        self.conversation_context.append({
            'type': 'ai_response',
            'input': text,
            'output': response,
            'goal': goal,
            'timestamp': time.time()
        })

        self.update_context_display()
        self.status_bar.config(text="AI response generated")

        if self.config.get('voice_feedback'):
            self.speak("Response generated")

    def process_with_goal(self, text, goal):
        """Process text based on selected goal using AI/ML logic"""
        # This is a rule-based system - in a real implementation,
        # this would use an actual ML model or call an API like GPT

        processors = {
            'writing': self.process_general_writing,
            'email': self.process_email,
            'code_doc': self.process_code_documentation,
            'notes': self.process_study_notes,
            'planning': self.process_task_planning,
            'creative': self.process_creative_writing,
            'research': self.process_research_summary,
            'report': self.process_report_writing
        }

        processor = processors.get(goal, self.process_general_writing)
        return processor(text)

    def process_general_writing(self, text):
        """Process for general writing goal"""
        response = f"""# General Writing Output

{text}

## Suggestions:
• Consider adding more descriptive details
• Break into shorter paragraphs for readability
• Review for clarity and conciseness

## Word Count: {len(text.split())} words
"""
        return response

    def process_email(self, text):
        """Process for professional email goal"""
        response = f"""Subject: [Your Subject Here]

Dear [Recipient],

{text}

Best regards,
[Your Name]

---
💡 Email Tips:
• Clear subject line
• Professional greeting and closing
• Concise and to the point
• Proofread before sending
"""
        return response

    def process_code_documentation(self, text):
        """Process for code documentation goal"""
        response = f"""```
/**
 * {text}
 *
 * @description [Brief description]
 * @param {{type}} paramName - Parameter description
 * @returns {{type}} Return value description
 * @example
 * // Example usage here
 */
```

## Documentation Guidelines:
• Clear parameter descriptions
• Return value documentation
• Usage examples
• Edge cases and limitations
"""
        return response

    def process_study_notes(self, text):
        """Process for study notes goal"""
        # Extract key points
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        response = f"""# Study Notes

## Main Content:
{text}

## Key Points:
"""
        for i, sentence in enumerate(sentences[:5], 1):
            response += f"{i}. {sentence}\n"

        response += """
## Review Questions:
• What are the main concepts?
• How does this connect to previous topics?
• What examples illustrate these points?

## Next Steps:
• Review and summarize in your own words
• Create flashcards for key terms
• Practice with examples
"""
        return response

    def process_task_planning(self, text):
        """Process for task planning goal"""
        # Extract tasks (simple heuristic)
        tasks = [s.strip() for s in text.split('.') if s.strip()]

        response = """# Task Plan

## Objectives:
"""
        for i, task in enumerate(tasks, 1):
            response += f"{i}. [ ] {task}\n"

        response += """
## Timeline:
• Start Date: [Today]
• Target Completion: [Set deadline]

## Resources Needed:
• [List resources]

## Success Criteria:
• [Define success metrics]
"""
        return response

    def process_creative_writing(self, text):
        """Process for creative writing goal"""
        response = f"""# Creative Writing Draft

{text}

## Story Elements:
• Setting: [Describe the setting]
• Characters: [List main characters]
• Conflict: [What's the central conflict?]
• Theme: [What's the underlying theme?]

## Enhancement Ideas:
• Add sensory details (sight, sound, smell, touch, taste)
• Develop character motivations
• Create stronger imagery
• Build tension and pacing
"""
        return response

    def process_research_summary(self, text):
        """Process for research summary goal"""
        response = f"""# Research Summary

## Overview:
{text}

## Key Findings:
• [Finding 1]
• [Finding 2]
• [Finding 3]

## Methodology:
• [Research methods used]

## Conclusions:
• [Main conclusions]

## Further Research:
• [Areas for additional study]

## Citations:
• [List sources]
"""
        return response

    def process_report_writing(self, text):
        """Process for report writing goal"""
        response = f"""# Report

## Executive Summary
{text}

## Introduction
[Background and context]

## Analysis
[Detailed analysis]

## Findings
• Finding 1
• Finding 2
• Finding 3

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## Conclusion
[Summary and next steps]
"""
        return response

    def improve_text(self):
        """Improve the transcribed text"""
        text = self.transcribed_text

        if not text.strip():
            messagebox.showwarning("No Text", "Please dictate some text first")
            return

        # Simple improvements (in real implementation, use ML)
        improved = text.strip()

        # Capitalize sentences
        improved = '. '.join(s.strip().capitalize() for s in improved.split('.'))

        # Remove extra spaces
        improved = re.sub(r'\s+', ' ', improved)

        # Update transcription
        self.transcription_text.delete('1.0', 'end')
        self.transcription_text.insert('1.0', improved)
        self.transcribed_text = improved

        self.status_bar.config(text="Text improved")
        self.speak("Text improved")

    def summarize_text(self):
        """Summarize the transcribed text"""
        text = self.transcribed_text

        if not text.strip():
            messagebox.showwarning("No Text", "Please dictate some text first")
            return

        # Simple summarization (extract key sentences)
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        # Take first and last sentences as summary
        if len(sentences) > 2:
            summary = f"{sentences[0]}. {sentences[-1]}."
        else:
            summary = text

        summary_response = f"""# Summary

{summary}

**Original length:** {len(text.split())} words
**Summary length:** {len(summary.split())} words
"""

        self.response_text.delete('1.0', 'end')
        self.response_text.insert('1.0', summary_response)

        self.status_bar.config(text="Text summarized")
        self.speak("Summary generated")

    def update_context_display(self):
        """Update context display"""
        self.context_text.delete('1.0', 'end')

        for item in self.conversation_context[-10:]:  # Last 10 items
            timestamp = datetime.fromtimestamp(item['timestamp']).strftime('%H:%M:%S')
            item_type = item['type']

            if item_type == 'transcription':
                self.context_text.insert('end', f"[{timestamp}] Transcribed: {item['text'][:100]}...\n\n")
            elif item_type == 'ai_response':
                self.context_text.insert('end', f"[{timestamp}] AI Response generated for goal: {item['goal']}\n\n")
            elif item_type == 'goal_change':
                self.context_text.insert('end', f"[{timestamp}] Goal changed to: {item['goal']}\n\n")

    def update_insights(self):
        """Update learning insights display"""
        self.insights_text.delete('1.0', 'end')

        insights = f"""📊 Learning Statistics:

• Total sessions: {len(self.conversation_context)}
• Preferred goal: {self.get_most_used_goal()}
• Writing style: {self.learning_data['writing_style']['tone']}
• Average transcription length: {self.get_avg_length()} words

💡 Personalization:
• The AI is learning your preferences
• Response quality improves over time
• Provide ratings to enhance learning

🎯 Recommendations:
• Practice regular dictation for better accuracy
• Use specific goals for better structure
• Review and refine generated content
"""

        self.insights_text.insert('1.0', insights)

    def get_most_used_goal(self):
        """Get most frequently used goal"""
        goal_counts = {}

        for item in self.conversation_context:
            if 'goal' in item:
                goal = item['goal']
                goal_counts[goal] = goal_counts.get(goal, 0) + 1

        if goal_counts:
            return max(goal_counts, key=goal_counts.get)
        return 'None'

    def get_avg_length(self):
        """Get average transcription length"""
        lengths = [len(item['text'].split()) for item in self.conversation_context if item['type'] == 'transcription']

        if lengths:
            return sum(lengths) // len(lengths)
        return 0

    def rate_response(self, rating):
        """Rate the AI response"""
        # Store rating for learning
        if self.conversation_context:
            last_response = next((item for item in reversed(self.conversation_context) if item['type'] == 'ai_response'), None)

            if last_response:
                last_response['rating'] = rating
                self.save_learning_data()

                messagebox.showinfo("Thank You", f"Rating saved: {'⭐' * rating}\n\nYour feedback helps improve the AI!")

    def clear_all(self):
        """Clear all text areas"""
        if messagebox.askyesno("Clear All", "Clear all text and start fresh?"):
            self.transcription_text.delete('1.0', 'end')
            self.response_text.delete('1.0', 'end')
            self.transcribed_text = ""
            self.conversation_context = []
            self.update_context_display()
            self.status_bar.config(text="All cleared")

    def speak(self, text):
        """Speak text using TTS"""
        if self.tts_engine and self.config.get('voice_feedback'):
            def speak_thread():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    print(f"TTS error: {e}")

            threading.Thread(target=speak_thread, daemon=True).start()

    def show_installation_guide(self):
        """Show installation guide"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Installation Required")
        guide_window.geometry("600x400")

        text = tk.Text(guide_window, wrap=tk.WORD, padx=20, pady=20)
        text.pack(fill=tk.BOTH, expand=True)

        guide_text = """AI Dictation Assistant Installation Guide

Required libraries for full functionality:

1. Speech Recognition:
   pip install SpeechRecognition

2. PyAudio (for microphone):
   # Ubuntu/Debian:
   sudo apt-get install portaudio19-dev python3-pyaudio
   pip install pyaudio

3. Text-to-Speech:
   pip install pyttsx3

4. Optional - for enhanced AI:
   pip install transformers torch

Features:
• Voice-to-text transcription
• Goal-based structured responses
• AI-powered text improvement
• Context-aware suggestions
• Learning from user feedback
• Multiple goal templates
• Auto-punctuation and capitalization

For more information:
https://pypi.org/project/SpeechRecognition/
"""

        text.insert('1.0', guide_text)
        text.config(state=tk.DISABLED)

        tk.Button(guide_window, text="Close", command=guide_window.destroy, padx=20, pady=10).pack(pady=10)

    def run(self):
        """Run dictation assistant"""
        self.root.mainloop()

if __name__ == '__main__':
    app = AI_DictationAssistant()
    app.run()
