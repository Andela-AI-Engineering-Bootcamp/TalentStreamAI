"""MCP Server for TalentStreamAI using LangGraph."""

from typing import Any, Literal
from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph

from app.tools.job_fetcher import fetch_job_description
from app.tools.resume_parser import parse_resume
from app.tools.ats_scorer import ats_score_resume


class TalentStreamState(TypedDict):
    """State for TalentStreamAI workflow."""

    job_url: str | None
    resume_file: str | None
    resume_ext: str | None
    job_data: dict | None
    resume_data: dict | None
    ats_score: dict | None
    gap_analysis: dict | None
    tailored_resume: str | None
    cover_letter: str | None
    email_draft: str | None
    error: str | None


class MCPServer:
    """MCP Server exposing TalentStreamAI tools via LangGraph."""

    def __init__(self):
        self.graph = self._build_graph()
        self.tools = {
            "fetch_job_description": self._wrap_tool(fetch_job_description),
            "parse_resume": self._wrap_tool(parse_resume),
            "ats_score_resume": self._wrap_tool(ats_score_resume),
        }

    def _wrap_tool(self, tool):
        """Wrap LangChain tool for MCP."""
        tool_schema = {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.args_schema,
        }

        async def execute(**kwargs):
            result = tool.invoke(kwargs)
            return result

        return {
            "schema": tool_schema,
            "execute": execute,
        }

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""

        def fetch_job(state: TalentStreamState) -> TalentStreamState:
            url = state.get("job_url")
            if not url:
                return {"error": "No job URL provided"}

            try:
                result = fetch_job_description.invoke({"url": url})
                return {"job_data": result}
            except Exception as e:
                return {"error": f"Failed to fetch job: {str(e)}"}

        def parse_resume(state: TalentStreamState) -> TalentStreamState:
            file_content = state.get("resume_file")
            file_ext = state.get("resume_ext")

            if not file_content or not file_ext:
                return {"error": "No resume file provided"}

            try:
                result = parse_resume.invoke(
                    {
                        "file_content": file_content,
                        "file_extension": file_ext,
                    }
                )
                return {"resume_data": result}
            except Exception as e:
                return {"error": f"Failed to parse resume: {str(e)}"}

        def score_resume(state: TalentStreamState) -> TalentStreamState:
            job_data = state.get("job_data")
            resume_data = state.get("resume_data")

            if not job_data or not resume_data:
                return {"error": "Missing job or resume data"}

            try:
                result = ats_score_resume.invoke(
                    {
                        "resume_data": resume_data,
                        "job_data": job_data,
                    }
                )
                return {"ats_score": result}
            except Exception as e:
                return {"error": f"Failed to score resume: {str(e)}"}

        def aggregate_gap_analysis(state: TalentStreamState) -> TalentStreamState:
            ats_score = state.get("ats_score", {})
            resume_data = state.get("resume_data", {})
            job_data = state.get("job_data", {})

            gap_analysis = {
                "keyword_gaps": ats_score.get("keyword_gaps", []),
                "skill_gaps": ats_score.get("skill_gaps", []),
                "experience_gap": ats_score.get("experience", {}),
                "education_gap": ats_score.get("education", {}),
                "recommendations": ats_score.get("recommendations", []),
            }

            return {"gap_analysis": gap_analysis}

        def should_generate_documents(
            state: TalentStreamState,
        ) -> Literal["generate", "skip"]:
            if state.get("error"):
                return "skip"
            if state.get("gap_analysis"):
                return "generate"
            return "skip"

        graph = StateGraph(TalentStreamState)

        graph.add_node("fetch_job", fetch_job)
        graph.add_node("parse_resume", parse_resume)
        graph.add_node("score_resume", score_resume)
        graph.add_node("aggregate_gap_analysis", aggregate_gap_analysis)

        graph.set_entry_point("fetch_job")
        graph.add_edge("fetch_job", "parse_resume")
        graph.add_edge("parse_resume", "score_resume")
        graph.add_edge("score_resume", "aggregate_gap_analysis")
        graph.add_edge("aggregate_gap_analysis", END)

        return graph.compile()

    async def run_workflow(
        self,
        job_url: str,
        resume_file: str,
        resume_ext: str,
    ) -> dict[str, Any]:
        """Run the complete TalentStreamAI workflow."""

        initial_state: TalentStreamState = {
            "job_url": job_url,
            "resume_file": resume_file,
            "resume_ext": resume_ext,
            "job_data": None,
            "resume_data": None,
            "ats_score": None,
            "gap_analysis": None,
            "tailored_resume": None,
            "cover_letter": None,
            "email_draft": None,
            "error": None,
        }

        result = await self.graph.ainvoke(initial_state)
        return result

    def get_tool_schemas(self) -> list[dict]:
        """Get tool schemas for MCP registration."""
        return [tool["schema"] for tool in self.tools.values()]

    async def execute_tool(self, tool_name: str, params: dict) -> Any:
        """Execute a specific tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool = self.tools[tool_name]
        return await tool["execute"](**params)


mcp_server = MCPServer()
