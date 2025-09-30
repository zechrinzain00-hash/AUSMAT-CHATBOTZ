import React, { useState, useCallback, useMemo } from 'react';
import { RefreshCw, CheckCircle, XCircle, ChevronRight, Zap } from 'lucide-react';

// --- API Configuration ---
const MODEL_NAME = "gemini-2.5-flash-preview-05-20";
const API_KEY = ""; 
const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${API_KEY}`;

// --- JSON Schema for Structured Quiz Generation ---
const QUIZ_SCHEMA = {
    type: "ARRAY",
    items: {
        type: "OBJECT",
        properties: {
            "question": { "type": "STRING", "description": "The trivia question." },
            "options": {
                "type": "ARRAY",
                "items": { "type": "STRING" },
                "description": "Exactly four possible answers for the question."
            },
            "correctIndex": { "type": "INTEGER", "description": "The 0-based index (0, 1, 2, or 3) of the correct answer within the options array." }
        },
        required: ["question", "options", "correctIndex"]
    }
};

/**
 * Custom hook for exponential backoff fetching.
 */
const useApiFetch = () => {
    const fetchWithBackoff = useCallback(async (payload, maxRetries = 5) => {
        let lastError = null;
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                const jsonText = result?.candidates?.[0]?.content?.parts?.[0]?.text;
                
                if (jsonText) {
                    try {
                        return JSON.parse(jsonText);
                    } catch (e) {
                        throw new Error("Failed to parse JSON response from model.");
                    }
                }
                
                throw new Error("Model response content was empty or malformed.");

            } catch (error) {
                lastError = error;
                const delay = Math.pow(2, attempt) * 1000;
                if (attempt < maxRetries - 1) {
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }
        console.error("API call failed after max retries:", lastError);
        throw new Error("Failed to generate content. Please try again.");
    }, []);

    return fetchWithBackoff;
};


// --- Main Application Component ---

export default function App() {
    const fetchWithBackoff = useApiFetch();
    
    // State for quiz generation
    const [topic, setTopic] = useState('World History');
    const [numQuestions, setNumQuestions] = useState(5);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // State for the quiz game
    const [quiz, setQuiz] = useState(null);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [selectedOption, setSelectedOption] = useState(null);
    const [isAnswerRevealed, setIsAnswerRevealed] = useState(false);

    const currentQuestion = useMemo(() => 
        quiz ? quiz[currentQuestionIndex] : null
    , [quiz, currentQuestionIndex]);

    const isQuizComplete = useMemo(() => 
        quiz && currentQuestionIndex === quiz.length
    , [quiz, currentQuestionIndex]);


    const generateQuiz = useCallback(async () => {
        if (loading) return;

        setLoading(true);
        setError(null);
        setQuiz(null);
        setCurrentQuestionIndex(0);
        setScore(0);
        setSelectedOption(null);
        setIsAnswerRevealed(false);

        const prompt = `Generate ${numQuestions} multiple-choice trivia questions about "${topic}". Each question must have exactly 4 options.`;

        const payload = {
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: QUIZ_SCHEMA
            },
        };

        try {
            const newQuiz = await fetchWithBackoff(payload);
            if (newQuiz && Array.isArray(newQuiz) && newQuiz.length > 0) {
                setQuiz(newQuiz);
            } else {
                setError("Quiz generation returned no questions. Try a different topic.");
            }
        } catch (err) {
            setError(err.message || "An unexpected error occurred during quiz generation.");
        } finally {
            setLoading(false);
        }
    }, [topic, numQuestions, loading, fetchWithBackoff]);

    const handleOptionSelect = (index) => {
        if (isAnswerRevealed) return;
        setSelectedOption(index);
    };

    const revealAnswer = () => {
        if (isAnswerRevealed || selectedOption === null) return;
        
        setIsAnswerRevealed(true);
        const correct = currentQuestion.correctIndex === selectedOption;
        
        if (correct) {
            setScore(prev => prev + 1);
        }
    };

    const nextQuestion = () => {
        if (currentQuestionIndex < quiz.length) {
            setCurrentQuestionIndex(prev => prev + 1);
            setSelectedOption(null);
            setIsAnswerRevealed(false);
        }
    };

    const getOptionClasses = (index) => {
        let classes = 'p-3 my-2 text-left rounded-lg transition duration-200 shadow-md';
        const isSelected = selectedOption === index;
        const isCorrect = currentQuestion?.correctIndex === index;

        if (!isAnswerRevealed) {
            // Before revealing
            classes += isSelected 
                ? ' bg-indigo-500 text-white border-4 border-indigo-700'
                : ' bg-white text-gray-800 hover:bg-indigo-50 border border-gray-200';
        } else {
            // After revealing
            if (isCorrect) {
                classes += ' bg-green-500 text-white font-bold border-4 border-green-700';
            } else if (isSelected) {
                classes += ' bg-red-500 text-white line-through border-4 border-red-700';
            } else {
                classes += ' bg-white text-gray-400 border border-gray-200 cursor-default opacity-50';
            }
        }
        return classes;
    };

    return (
        <div className="min-h-screen bg-gray-100 p-4 sm:p-8 flex items-center justify-center">
            <div className="w-full max-w-lg bg-white p-6 sm:p-8 rounded-2xl shadow-2xl">
                <header className="text-center mb-6">
                    <h1 className="text-4xl font-extrabold text-indigo-700 flex items-center justify-center">
                        <Zap className="w-8 h-8 mr-2 text-yellow-500" />
                        AI Trivia Bot
                    </h1>
                    <p className="text-gray-500 mt-1">Powered by Gemini - Custom Quizzes!</p>
                </header>

                {/* Quiz Generation Controls */}
                <div className="bg-indigo-50 p-4 rounded-xl mb-6 shadow-inner">
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-indigo-700 mb-1">
                            Trivia Topic
                        </label>
                        <input
                            type="text"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            placeholder="e.g., Space Exploration, 90s Music, Python"
                            className="w-full p-3 border border-indigo-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                            disabled={loading}
                        />
                    </div>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-indigo-700 mb-1">
                            Number of Questions (Max 10)
                        </label>
                        <input
                            type="number"
                            value={numQuestions}
                            onChange={(e) => setNumQuestions(Math.min(10, Math.max(1, parseInt(e.target.value) || 1)))}
                            min="1"
                            max="10"
                            className="w-full p-3 border border-indigo-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                            disabled={loading}
                        />
                    </div>
                    
                    <button
                        onClick={generateQuiz}
                        disabled={loading || !topic}
                        className="w-full flex items-center justify-center bg-indigo-600 text-white font-semibold py-3 px-4 rounded-xl hover:bg-indigo-700 transition duration-300 disabled:bg-indigo-300 shadow-lg"
                    >
                        {loading ? (
                            <>
                                <RefreshCw className="w-5 h-5 mr-2 animate-spin" /> Generating Quiz...
                            </>
                        ) : (
                            "Generate New Quiz"
                        )}
                    </button>
                </div>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-xl mb-4" role="alert">
                        <p className="font-bold">Error</p>
                        <p className="text-sm">{error}</p>
                    </div>
                )}
                
                {/* Quiz Display */}
                {quiz && !isQuizComplete && currentQuestion && (
                    <div className="quiz-container">
                        <div className="flex justify-between items-center mb-4 text-gray-600">
                            <span className="text-xl font-bold text-indigo-600">
                                Question {currentQuestionIndex + 1} / {quiz.length}
                            </span>
                            <span className="text-lg font-medium">
                                Score: {score}
                            </span>
                        </div>
                        
                        <div className="bg-indigo-100 p-4 sm:p-6 rounded-xl mb-6 shadow-md">
                            <p className="text-lg font-semibold text-gray-800">
                                {currentQuestion.question}
                            </p>
                        </div>

                        {/* Options */}
                        <div className="flex flex-col">
                            {currentQuestion.options.map((option, index) => (
                                <button
                                    key={index}
                                    onClick={() => handleOptionSelect(index)}
                                    disabled={isAnswerRevealed || loading}
                                    className={getOptionClasses(index)}
                                >
                                    <span className="font-mono text-xs mr-2">{String.fromCharCode(65 + index)}.</span> 
                                    {option}
                                </button>
                            ))}
                        </div>

                        {/* Action Buttons */}
                        <div className="mt-6 flex justify-between space-x-4">
                            <button
                                onClick={revealAnswer}
                                disabled={selectedOption === null || isAnswerRevealed}
                                className="flex-1 flex items-center justify-center bg-green-500 text-white font-semibold py-3 px-4 rounded-xl hover:bg-green-600 transition disabled:bg-green-300"
                            >
                                <CheckCircle className="w-5 h-5 mr-2" />
                                Check Answer
                            </button>
                            
                            <button
                                onClick={nextQuestion}
                                disabled={!isAnswerRevealed || currentQuestionIndex === quiz.length - 1}
                                className="flex-1 flex items-center justify-center bg-gray-500 text-white font-semibold py-3 px-4 rounded-xl hover:bg-gray-600 transition disabled:bg-gray-300"
                            >
                                Next Question
                                <ChevronRight className="w-5 h-5 ml-2" />
                            </button>
                        </div>
                    </div>
                )}
                
                {/* Completion Screen */}
                {isQuizComplete && quiz && (
                    <div className="text-center p-8 bg-indigo-50 rounded-xl shadow-inner">
                        <h2 className="text-3xl font-bold text-indigo-600 mb-4">Quiz Finished!</h2>
                        <p className="text-2xl mb-6">
                            Final Score: <span className="text-green-600 font-extrabold">{score} / {quiz.length}</span>
                        </p>
                        <button
                            onClick={generateQuiz}
                            className="flex items-center mx-auto bg-indigo-600 text-white font-semibold py-3 px-6 rounded-xl hover:bg-indigo-700 transition shadow-lg"
                        >
                            <RefreshCw className="w-5 h-5 mr-2" />
                            Play Again
                        </button>
                    </div>
                )}

                {/* Initial State / No Quiz */}
                {!quiz && !loading && !error && (
                    <div className="text-center p-8 text-gray-500 border-2 border-dashed border-gray-300 rounded-xl">
                        <p className="text-lg">Enter a topic above and click "Generate New Quiz" to start!</p>
                    </div>
                )}
            </div>
        </div>
    );
}


