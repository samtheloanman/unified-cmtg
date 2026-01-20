# Phase F.6 Content Generation Checklist

## Infrastructure
- [x] **Secure Environment**: Rotate API keys and configure `.env.local`
- [x] **Dependency Update**: Add `reportlab` to `requirements.txt`
- [x] **Service Layer**: Implement `AiContentGenerator` with Gemini 2.0 support
- [x] **Dynamic Personas**: Implement logic to map keywords to expert personas

## Master Data
- [x] **Program Hierarchy**: Define 100+ programs in `program_hierarchy.md`
- [x] **Shell Creation**: Run `create_program_shells` to ensure DB existence

## Generation Commands
- [x] **Local Generation**: `generate_local_pages` command with proximity logic
- [x] **Program Content**: `generate_program_content` command with full-page JSON support

## Execution
- [x] **Test Run**: Verify "Super Jumbo" content generation
- [x] **Batch Execution**: Run for priority groups (Jumbo, Non-QM, Commercial)
- [x] **Validation**: Verify schema markup and HTML rendering
