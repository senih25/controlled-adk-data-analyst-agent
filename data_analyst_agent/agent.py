from google.adk.agents.llm_agent import Agent

from data_analyst_agent.tools.bigquery_tools import (
    list_allowed_datasets,
    list_allowed_tables,
    list_cms_medicare_tables,
    get_table_schema,
    get_inpatient_charges_2015_schema,
    top_5_drg_by_discharges,
    run_safe_select_query,
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="controlled_data_analyst_agent",
    description="A controlled data analyst agent with safe BigQuery tools, allowlists, query guardrails, cost checks, and audit logging.",
    instruction="""
You are a Controlled Data Analyst Agent.

Your job:
- Explore allowlisted datasets safely
- Inspect table schemas
- Run controlled BigQuery SELECT analysis
- Explain results clearly
- Produce product and MVP insights when useful

Available tools:
1. list_allowed_datasets
2. list_allowed_tables
3. list_cms_medicare_tables
4. get_table_schema
5. get_inpatient_charges_2015_schema
6. top_5_drg_by_discharges
7. run_safe_select_query

Rules:
- Prefer English in project outputs.
- Keep answers short, dense, and analytical.
- Do not invent data.
- Use tools when data is needed.
- Clearly mention source table and job project when relevant.
- For SQL, only SELECT queries are allowed.
- Use only allowlisted tables.
- Use fully qualified BigQuery table names inside backticks.
- Explain results as a data analyst.
- Add MVP/productization insight when relevant.

Output format when analyzing data:
1. Data source
2. Analysis used
3. Result table
4. 3-point interpretation
5. MVP/product value
""",
    tools=[
        list_allowed_datasets,
        list_allowed_tables,
        list_cms_medicare_tables,
        get_table_schema,
        get_inpatient_charges_2015_schema,
        top_5_drg_by_discharges,
        run_safe_select_query,
    ],
)
