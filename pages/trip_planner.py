from crewai import Agent
from fpdf import FPDF
import re
import streamlit as st
import datetime
import sys
from crewai import Task
from textwrap import dedent
from datetime import date
from langchain_core.language_models.chat_models import BaseChatModel
from crewai import Crew, LLM
from pages.tools.calculator_tool import CalculatorTools
from pages.tools.browser_tool import BrowserTools
from pages.tools.search_tool import SearchTools
from pages.tools.stream import StreamToExpander
import os
from dotenv import load_dotenv
load_dotenv()
os.environ['GEMINI_API_KEY']=os.getenv('GEMINI_API_KEY')

# llm=LLM(model='gemini/gemini-2.0-flash')
def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

class TripCrew:

    def __init__(self, origin, cities, date_range, interests):
        self.cities = cities
        self.origin = origin
        self.interests = interests
        # Convert date_range to string format for better handling
        self.date_range = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
        self.output_placeholder = st.empty()
        self.llm = LLM(model="gemini/gemini-2.0-flash")
        # self.llm = OpenAI(
        #     temperature=0.7,
        #     model_name="gpt-4",
        # )

    def run(self,origin,cities,date_range,interests):
        try:
            search_tool = SearchTools()
            browser_tool = BrowserTools()
            calculator_tool = CalculatorTools()

            city_selector_agent = Agent(
                        role='City Selection Expert',
                        goal='Select the best city based on weather, season, and prices',
                        backstory='An expert in analyzing travel data to pick ideal destinations',
                        tools=[search_tool, browser_tool],
                        allow_delegation=False,
                        llm=self.llm,
                        # verbose=True
                    )
            local_expert_agent =  Agent(
                        role='Local Expert at this city',
                        goal='Provide the BEST insights about the selected city',
                        backstory="""A knowledgeable local guide with extensive information
                                    about the city, it's attractions and customs""",
                        tools=[search_tool, browser_tool],
                        allow_delegation=False,
                        llm=self.llm,
                        # verbose=True
                    )
            travel_concierge_agent = Agent(
                        role='Amazing Travel Concierge',
                        goal="""Create the most amazing travel itineraries with budget and 
                    packing suggestions for the city. Create a tabular budget in end""",
                        backstory="""Specialist in travel planning and logistics with 
                    decades of experience""",
                        tools=[search_tool, browser_tool, calculator_tool],
                        allow_delegation=False,
                        llm=self.llm,
                        # verbose=True
                    )

            identify_task=Task(description=dedent(f"""
                        Analyze and select the best city for the trip based
                        on specific criteria such as weather patterns, seasonal
                        events, and travel costs. This task involves comparing
                        multiple cities, considering factors like current weather
                        conditions, upcoming cultural or seasonal events, and
                        overall travel expenses.

                        Your final answer must be a detailed
                        report on the chosen city, and everything you found out
                        about it, including the actual flight costs, weather
                        forecast and attractions.
                        If you do your BEST WORK, I'll tip you $100 and grant you any wish you want!

                        Traveling from: {self.origin}
                        City Options: {self.cities}
                        Trip Date: {self.date_range}
                        Traveler Interests: {self.interests}
                    """),
                        expected_output="A detailed report on the chosen city with flight costs, weather forecast, and attractions.",
                        agent=city_selector_agent)

            gather_task=Task(description=dedent(f"""
                        As a local expert on this city you must compile an
                        in-depth guide for someone traveling there and wanting
                        to have THE BEST trip ever!
                        Gather information about  key attractions, local customs,
                        special events, and daily activity recommendations.
                        Find the best spots to go to, the kind of place only a
                        local would know.
                        This guide should provide a thorough overview of what
                        the city has to offer, including hidden gems, cultural
                        hotspots, must-visit landmarks, weather forecasts, and
                        high level costs.

                        The final answer must be a comprehensive city guide,
                        rich in cultural insights and practical tips,
                        tailored to enhance the travel experience.
                        If you do your BEST WORK, I'll tip you $100 and grant you any wish you want!

                        Trip Date: {self.date_range}
                        Traveling from: {self.origin}
                        Traveler Interests: {self.interests}
                    """),
                        expected_output="A comprehensive city guide with cultural insights and practical tips.",
                        agent=local_expert_agent)

            plan_task=Task(description=dedent(f"""
                        Expand this guide into a full travel
                        itinerary for this time {self.date_range} with detailed per-day plans, including
                        weather forecasts, places to eat, packing suggestions,
                        and a budget breakdown.

                        You MUST suggest actual places to visit, actual hotels
                        to stay and actual restaurants to go to.

                        This itinerary should cover all aspects of the trip,
                        from arrival to departure, integrating the city guide
                        information with practical travel logistics.

                        Your final answer MUST be a complete expanded travel plan,
                        formatted as markdown, encompassing a daily schedule,
                        anticipated weather conditions, recommended clothing and
                        items to pack, and a detailed budget, ensuring THE BEST
                        TRIP EVER, Be specific and give it a reason why you picked
                        # up each place, what make them special! 
                        If you do your BEST WORK, I'll tip you $100 and grant you any wish you want!

                        Trip Date: {self.date_range}
                        Traveling from: {self.origin}
                        Traveler Interests: {self.interests}
                    """),
                        expected_output="A complete 7-day travel plan, formatted as markdown, with a daily schedule and budget.",
                        agent=travel_concierge_agent)

            crew = Crew(
                            agents=[
                                city_selector_agent, local_expert_agent, travel_concierge_agent
                            ],
                            tasks=[identify_task, gather_task, plan_task],
                            verbose=True
                        )
            result = crew.kickoff()
            self.output_placeholder.markdown(result)
            return result
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None


# if __name__ == "__main__":
#     icon("🏖️ VacAIgent")
icon("🏖️ VoyageAI")
st.subheader("Let AI agents plan your next vacation!", divider="rainbow", anchor=False)

# Inject custom CSS to style the input fields


today = datetime.datetime.now().date()
next_year = today.year + 1
jan_16_next_year = datetime.date(next_year, 1, 10)

# Move the form to the main page
st.header("👇 Enter your trip details")
with st.form("my_form"):
    location = st.text_input("Where are you currently located?", placeholder="San Mateo, CA")
    cities = st.text_input("City and country are you interested in vacationing at?", placeholder="Bali, Indonesia")
    date_range = st.date_input(
        "Date range you are interested in traveling?",
        min_value=today,
        value=(today, jan_16_next_year + datetime.timedelta(days=6)),
        format="MM/DD/YYYY",
    )
    interests = st.text_area("High level interests and hobbies or extra details about your trip?",
                             placeholder="2 adults who love swimming, dancing, hiking, and eating")
    submitted = st.form_submit_button("Submit")

st.divider()




if submitted:
    with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
        with st.container(height=500, border=False):
            sys.stdout = StreamToExpander(st)
            trip_crew = TripCrew(location, cities, date_range, interests)
            result = trip_crew.run(location,cities,date_range,interests)
        status.update(label="✅ Trip Plan Ready!",
                      state="complete", expanded=False)

    st.subheader("Here is your Trip Plan", anchor=False, divider="rainbow")
    st.markdown(result)

