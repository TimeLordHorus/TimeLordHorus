using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;

namespace Sanctuary.Verification
{
    /// <summary>
    /// Challenge question system for anti-bot verification
    /// Uses contextual knowledge questions that require human understanding
    /// Questions are culturally aware and require critical thinking
    /// </summary>
    public class ChallengeQuestionSystem : MonoBehaviour
    {
        [Header("Challenge Settings")]
        [SerializeField] private int passingScore = 2; // Out of 3 questions
        [SerializeField] private float questionTimeoutSeconds = 30f;
        [SerializeField] private bool shuffleQuestions = true;
        [SerializeField] private bool shuffleAnswers = true;

        // Events
        public event Action<bool, int, int> OnChallengesComplete; // passed, score, total
        public event Action<ChallengeQuestion, int> OnQuestionPresented; // question, questionNumber
        public event Action<bool> OnQuestionAnswered; // correct

        // Question pool
        private List<ChallengeQuestion> questionPool;
        private List<ChallengeQuestion> currentChallenges;
        private int currentQuestionIndex = 0;
        private int correctAnswers = 0;

        // State
        private bool isWaitingForAnswer = false;
        private DateTime questionStartTime;

        private void Awake()
        {
            InitializeQuestionPool();
        }

        /// <summary>
        /// Initialize question pool with age-appropriate challenges
        /// These require cultural/contextual knowledge that adults would have
        /// </summary>
        private void InitializeQuestionPool()
        {
            questionPool = new List<ChallengeQuestion>
            {
                // Historical events (1990s-2010s knowledge)
                new ChallengeQuestion
                {
                    questionText = "Which of these events happened first in history?",
                    answers = new List<string>
                    {
                        "The Moon landing (1969)",
                        "The first iPhone release (2007)",
                        "The fall of the Berlin Wall (1989)",
                        "The founding of Google (1998)"
                    },
                    correctAnswerIndex = 0,
                    category = QuestionCategory.Historical,
                    difficulty = 1
                },

                // Cultural references
                new ChallengeQuestion
                {
                    questionText = "Which classic novel was written first?",
                    answers = new List<string>
                    {
                        "1984 by George Orwell (1949)",
                        "The Hunger Games (2008)",
                        "Harry Potter (1997)",
                        "The Maze Runner (2009)"
                    },
                    correctAnswerIndex = 0,
                    category = QuestionCategory.Cultural,
                    difficulty = 1
                },

                // Real-world knowledge
                new ChallengeQuestion
                {
                    questionText = "Which of these requires a driver's license in most countries?",
                    answers = new List<string>
                    {
                        "Riding a bicycle",
                        "Operating a motor vehicle",
                        "Riding a horse",
                        "Using an electric scooter"
                    },
                    correctAnswerIndex = 1,
                    category = QuestionCategory.Practical,
                    difficulty = 1
                },

                // Financial literacy
                new ChallengeQuestion
                {
                    questionText = "What is typically required to open a bank account?",
                    answers = new List<string>
                    {
                        "Social media profile",
                        "Gaming account",
                        "Government-issued ID",
                        "School transcript"
                    },
                    correctAnswerIndex = 2,
                    category = QuestionCategory.Practical,
                    difficulty = 1
                },

                // Legal knowledge
                new ChallengeQuestion
                {
                    questionText = "In most democracies, what is the minimum voting age?",
                    answers = new List<string>
                    {
                        "16 years old",
                        "18 years old",
                        "21 years old",
                        "25 years old"
                    },
                    correctAnswerIndex = 1,
                    category = QuestionCategory.Legal,
                    difficulty = 1
                },

                // Historical figures
                new ChallengeQuestion
                {
                    questionText = "Who was the first person to walk on the Moon?",
                    answers = new List<string>
                    {
                        "Buzz Aldrin",
                        "Neil Armstrong",
                        "Yuri Gagarin",
                        "John Glenn"
                    },
                    correctAnswerIndex = 1,
                    category = QuestionCategory.Historical,
                    difficulty = 2
                },

                // Geography
                new ChallengeQuestion
                {
                    questionText = "Which ocean is the largest by surface area?",
                    answers = new List<string>
                    {
                        "Atlantic Ocean",
                        "Indian Ocean",
                        "Pacific Ocean",
                        "Arctic Ocean"
                    },
                    correctAnswerIndex = 2,
                    category = QuestionCategory.Geography,
                    difficulty = 1
                },

                // Technology history
                new ChallengeQuestion
                {
                    questionText = "What was invented first?",
                    answers = new List<string>
                    {
                        "The personal computer",
                        "The smartphone",
                        "The internet",
                        "Social media"
                    },
                    correctAnswerIndex = 0,
                    category = QuestionCategory.Technology,
                    difficulty = 2
                },

                // Science
                new ChallengeQuestion
                {
                    questionText = "What causes seasons on Earth?",
                    answers = new List<string>
                    {
                        "Distance from the Sun",
                        "Earth's tilt on its axis",
                        "Solar flares",
                        "The Moon's orbit"
                    },
                    correctAnswerIndex = 1,
                    category = QuestionCategory.Science,
                    difficulty = 2
                },

                // Legal age awareness
                new ChallengeQuestion
                {
                    questionText = "In most jurisdictions, you must be 18+ to:",
                    answers = new List<string>
                    {
                        "Attend school",
                        "Sign a legally binding contract",
                        "Use social media",
                        "Play video games"
                    },
                    correctAnswerIndex = 1,
                    category = QuestionCategory.Legal,
                    difficulty = 1
                },

                // Media literacy
                new ChallengeQuestion
                {
                    questionText = "Which statement about online information is most accurate?",
                    answers = new List<string>
                    {
                        "Everything on the internet is true",
                        "Wikipedia articles can be edited by anyone",
                        "Social media posts are always fact-checked",
                        "Images are proof that events happened"
                    },
                    correctAnswerIndex = 1,
                    category = QuestionCategory.MediaLiteracy,
                    difficulty = 2
                },

                // Environmental awareness
                new ChallengeQuestion
                {
                    questionText = "Which action helps reduce carbon emissions?",
                    answers = new List<string>
                    {
                        "Leaving lights on all night",
                        "Using public transportation",
                        "Running water continuously",
                        "Buying more plastic products"
                    },
                    correctAnswerIndex = 1,
                    category = QuestionCategory.Environmental,
                    difficulty = 1
                }
            };

            Debug.Log($"[ChallengeSystem] Initialized with {questionPool.Count} questions");
        }

        /// <summary>
        /// Present challenge questions to user
        /// </summary>
        public async Task<bool> PresentChallenges(int numberOfQuestions)
        {
            currentQuestionIndex = 0;
            correctAnswers = 0;
            currentChallenges = SelectRandomQuestions(numberOfQuestions);

            Debug.Log($"[ChallengeSystem] Presenting {numberOfQuestions} challenges");

            for (int i = 0; i < currentChallenges.Count; i++)
            {
                ChallengeQuestion question = currentChallenges[i];

                // Shuffle answers if enabled
                if (shuffleAnswers)
                {
                    ShuffleAnswers(ref question);
                }

                // Present question
                OnQuestionPresented?.Invoke(question, i + 1);

                // Wait for answer (with timeout)
                bool answered = await WaitForAnswer(question);

                if (!answered)
                {
                    Debug.LogWarning($"[ChallengeSystem] Question {i + 1} timeout");
                }
            }

            bool passed = correctAnswers >= passingScore;

            Debug.Log($"[ChallengeSystem] Challenges complete: {correctAnswers}/{currentChallenges.Count} ({(passed ? "PASS" : "FAIL")})");

            OnChallengesComplete?.Invoke(passed, correctAnswers, currentChallenges.Count);

            return passed;
        }

        /// <summary>
        /// Select random questions from pool
        /// </summary>
        private List<ChallengeQuestion> SelectRandomQuestions(int count)
        {
            List<ChallengeQuestion> selected = new List<ChallengeQuestion>();

            if (shuffleQuestions)
            {
                // Shuffle pool
                List<ChallengeQuestion> shuffled = new List<ChallengeQuestion>(questionPool);
                for (int i = 0; i < shuffled.Count; i++)
                {
                    int randomIndex = UnityEngine.Random.Range(i, shuffled.Count);
                    var temp = shuffled[i];
                    shuffled[i] = shuffled[randomIndex];
                    shuffled[randomIndex] = temp;
                }

                // Take first N questions
                selected = shuffled.Take(count).ToList();
            }
            else
            {
                // Take first N questions
                selected = questionPool.Take(count).ToList();
            }

            return selected;
        }

        /// <summary>
        /// Shuffle answers while tracking correct index
        /// </summary>
        private void ShuffleAnswers(ref ChallengeQuestion question)
        {
            string correctAnswer = question.answers[question.correctAnswerIndex];

            // Shuffle list
            for (int i = 0; i < question.answers.Count; i++)
            {
                int randomIndex = UnityEngine.Random.Range(i, question.answers.Count);
                var temp = question.answers[i];
                question.answers[i] = question.answers[randomIndex];
                question.answers[randomIndex] = temp;
            }

            // Find new index of correct answer
            question.correctAnswerIndex = question.answers.IndexOf(correctAnswer);
        }

        /// <summary>
        /// Wait for user to answer question
        /// </summary>
        private async Task<bool> WaitForAnswer(ChallengeQuestion question)
        {
            isWaitingForAnswer = true;
            questionStartTime = DateTime.UtcNow;

            // Wait for answer or timeout
            while (isWaitingForAnswer)
            {
                // Check timeout
                if ((DateTime.UtcNow - questionStartTime).TotalSeconds > questionTimeoutSeconds)
                {
                    isWaitingForAnswer = false;
                    OnQuestionAnswered?.Invoke(false);
                    return false;
                }

                await Task.Delay(100);
            }

            return true;
        }

        /// <summary>
        /// Submit answer to current question
        /// Called by UI when user selects an answer
        /// </summary>
        public void SubmitAnswer(int answerIndex)
        {
            if (!isWaitingForAnswer)
            {
                Debug.LogWarning("[ChallengeSystem] No question active");
                return;
            }

            ChallengeQuestion currentQuestion = currentChallenges[currentQuestionIndex];

            bool correct = answerIndex == currentQuestion.correctAnswerIndex;

            if (correct)
            {
                correctAnswers++;
                Debug.Log($"[ChallengeSystem] Correct answer! ({correctAnswers} total)");
            }
            else
            {
                Debug.Log("[ChallengeSystem] Incorrect answer");
            }

            isWaitingForAnswer = false;
            currentQuestionIndex++;

            OnQuestionAnswered?.Invoke(correct);
        }

        /// <summary>
        /// Get current question
        /// </summary>
        public ChallengeQuestion GetCurrentQuestion()
        {
            if (currentChallenges != null && currentQuestionIndex < currentChallenges.Count)
            {
                return currentChallenges[currentQuestionIndex];
            }

            return null;
        }

        /// <summary>
        /// Get current score
        /// </summary>
        public (int correct, int total) GetCurrentScore()
        {
            return (correctAnswers, currentQuestionIndex);
        }

#if UNITY_EDITOR
        [ContextMenu("Test Challenges")]
        private void EditorTestChallenges()
        {
            _ = PresentChallenges(3);
        }

        [ContextMenu("Submit Correct Answer")]
        private void EditorSubmitCorrect()
        {
            var question = GetCurrentQuestion();
            if (question != null)
            {
                SubmitAnswer(question.correctAnswerIndex);
            }
        }

        [ContextMenu("Submit Wrong Answer")]
        private void EditorSubmitWrong()
        {
            var question = GetCurrentQuestion();
            if (question != null)
            {
                int wrongIndex = (question.correctAnswerIndex + 1) % question.answers.Count;
                SubmitAnswer(wrongIndex);
            }
        }
#endif
    }

    /// <summary>
    /// Challenge question data structure
    /// </summary>
    [Serializable]
    public class ChallengeQuestion
    {
        public string questionText;
        public List<string> answers;
        public int correctAnswerIndex;
        public QuestionCategory category;
        public int difficulty; // 1-3
    }

    public enum QuestionCategory
    {
        Historical,
        Cultural,
        Practical,
        Legal,
        Geography,
        Technology,
        Science,
        MediaLiteracy,
        Environmental
    }
}
