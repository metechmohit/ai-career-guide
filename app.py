import streamlit as st 
import os
import requests ## for backened only 
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

OPENAI_API_KEY = st.secrets["key"]


llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.75)

# for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "questions" not in st.session_state:
    st.session_state.questions = None

#
main_prompt_template = """You are a career counsellor for an EdTech company. Use the conversation history to provide personalized advice to the student and try to make it short and in bullet points.

Conversation History:
{history}

Student: {user_input}
Counsellor:"""

def generate_prompt(conversation, user_input):
    history = "\n".join(conversation)
    return main_prompt_template.format(history=history, user_input=user_input)

def generate_questions(edu_prompt):
    question_prompt = f"Generate 5 questions to ask a student in {edu_prompt} about their interests, goals, and preferences."
    questions = llm(question_prompt)
    return questions.strip().split('\n')

# user interface
st.title("Hello 👋 Welcome to AI Career-Counsellor!")

name = st.text_input("Enter your name")
if name:
    st.write(f"Hello {name}! Let's clarify your doubts.")
    st.subheader("Enter Your Current Education Level")
    edu_prompt = st.radio(
        "Please select one:",
        ["High-School Junior", "College", "Professional"],
        index=None
    )
    st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

    if edu_prompt:
        problem_description = st.text_input("Describe the problem you are facing")
        if problem_description:
            hobby = st.text_input("Enter your favourite pastime hobby")
            if hobby:
                # Generate questions only if they haven't been generated in this session
                if st.session_state.questions is None:
                    st.session_state.questions = generate_questions(edu_prompt)

                questions = st.session_state.questions

                responses = []
                for i, question in enumerate(questions, 1):
                    st.subheader(f"{question}")
                    response = st.text_input(f"Answer for Question {i}")
                    responses.append(response)

                if all(responses):
                    # prompt for personality analysis
                    answer_stmt = (
                        f"Assume you are a career counsellor for {name}, a {edu_prompt} student. "
                        f"The student's problem description is: {problem_description}. Their hobby is {hobby}. "
                        f"Here are their responses to the questions: "
                    )
                    for i, response in enumerate(responses, 1):
                        answer_stmt += f"Question {i}: {questions[i-1]}, Answer: {response}. "

                    # Generate the full prompt
                    prompt = generate_prompt(st.session_state.conversation, answer_stmt)

                    # Run the personality analysis prompt
                    personality_type = llm(prompt)

                    st.session_state.conversation.append(f"Student: {answer_stmt}")
                    st.session_state.conversation.append(f"Counsellor: {personality_type}")

                    # Display personality type
                    st.write(f"The personality type is: {personality_type}")

                    # Generate prompt for career advice based on personality type
                    goals = (
                        f"Based on the personality type '{personality_type}', suggest the top 5 career options for {name}. "
                        f"Provide the name of the profession and a short description (max 15 words) for each."
                    )

                    career_options = llm(goals)
                    st.subheader("Some great career options for you could be:")
                    st.write(career_options)

                    # Append career advice to the conversation history
                    st.session_state.conversation.append(f"Student: {goals}")
                    st.session_state.conversation.append(f"Counsellor: {career_options}")

            else:
                st.subheader("Please enter your favourite pastime hobby to continue.")
        else:
            st.subheader("Please describe the problem you are facing to continue.")
    else:
        st.subheader("Please select your current education level to continue.")

# Display conversation history
st.header("Conversation History")
for message in st.session_state.conversation:
    st.write(message)

# Button to clear the conversation history
if st.button("Clear Conversation"):
    st.session_state.conversation = []
    st.session_state.questions = None
    st.experimental_rerun()
