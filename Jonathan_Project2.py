import streamlit as st
#from langchain_ollama import ChatOllama
from pdfminer.high_level import extract_text
import time

#-----------------------------------
#This is the form that gathers user input

st.image("cortana.jpg",width=100)
st.title("Input to AI")

file = st.file_uploader("Upload attachment:")
question = st.text_input("Enter your question:")
llm_type = st.radio("Select LLM: ", ["Llama","Gemini (requires key)","ChatGPT (requires key)"])
if llm_type in ["ChatGPT (requires key)","Gemini (requires key)"]:
	key = st.text_input("Key please")
abbreviation_index = st.radio("Include abbreviation index: ", ["No","Yes"])
if abbreviation_index == "Yes":
	abbreviation_index = True
else:
	abbreviation_index = False

#-----------------------------------
#Creats a button to process input
if st.button("Submit"):

	#Starting a timer to track how long it takes to respond
	start_time = time.time()
	st.write(f"Start time: {start_time:.2f}")	

	#Creating a variable that will be sent to the LLM
	prompt = ""

	#We start with the file. If there is a file, it will put it in
	#the prompt variable and add a line
	if file is not None:
		#creates a string of the information in the submitted file
		text = extract_text(file)

		#Testing the size limit of the LLM
		numbered = []
		for i, line in enumerate(text.split("\n")):
			numbered.append(f"{i+1:04d}: {line}\n")
		main_text = "\n".join(numbered)
		prompt += main_text[:29000] + "\n--------------" 

	#This adds instructions and the question to the prompt
	prompt += "\nPlease answer the users question below using anything above as context."
	prompt += "\nIf there is nothing above then just focus on the question."
	prompt += f"\n{question}"

	#This add more instructions if abbreviation index option was selected
	if abbreviation_index:
		prompt += f"\n---------" + f"\nAlso please generate a abbreviation index in the example below"		
		prompt += "\nWDC: weighted degree centrality"

	#Determine which LLM was selected and give it the prompt. Then capture the response
	#in the variable ai_response
	if llm_type == "Llama":
		import subprocess

		response = subprocess.run(
			["ollama", "run", "mistral"],
			input=prompt.encode(),
			stdout=subprocess.PIPE
		)

		ai_response = response.stdout.decode()
	
	elif llm_type == "ChatGPT (requires key)":
		from openai import OpenAI
		
		#My API key for ChatGPT
		client = OpenAI(api_key=key)

		response = client.chat.completions.create(
    			model="gpt-4.1",    # or gpt-4o, gpt-4.1-mini, etc.
    			messages=[{"role": "user", "content": prompt}]
		)

		ai_response = response.choices[0].message.content


	else:
		import google.generativeai as genai
		
		genai.configure(api_key=key)
		model = genai.GenerativeModel("gemini-2.0-flash")

		response = model.generate_content(prompt)
		ai_response = response.text
	
	#Calculating the time it took to respond
	end_time =time.time()
	st.write(f"End time: {end_time:.2f}")
	st.write(f"Total Time: {(end_time - start_time)/60:.2f} minutes")

	st.subheader("AI Response:")
	st.text(ai_response)