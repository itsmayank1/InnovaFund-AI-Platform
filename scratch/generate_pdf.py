import os
from fpdf import FPDF

class ShowcasePDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(2, 132, 199) # Cobalt Blue accent
        self.cell(0, 10, 'InnovaFund AI - Milestone 1 Final Showcase & Evaluator Guide', border=0, new_x="LMARGIN", new_y="NEXT", align='L')
        self.set_draw_color(200, 200, 200)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Enterprise AI Innovation Intelligence Platform', border=0, align='C')

def create_pdf(output_path):
    pdf = ShowcasePDF(orientation='P', unit='mm', format='A4')
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Document Title
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, 'InnovaFund AI - Milestone 1 Final Presentation Guide', border=0, new_x="LMARGIN", new_y="NEXT", align='L')
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, 'Project: InnovaFund AI - Enterprise AI-Powered Funding & Innovation Intelligence Platform', border=0, new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.ln(5)

    def section_title(title):
        pdf.set_font('Helvetica', 'B', 11.5)
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(2, 132, 199) # Cobalt Blue
        pdf.cell(0, 8, f'  {title}', border=0, new_x="LMARGIN", new_y="NEXT", align='L', fill=True)
        pdf.ln(3)

    def sub_title(title):
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 6, title, border=0, new_x="LMARGIN", new_y="NEXT", align='L')
        pdf.ln(1)

    def body_text(text):
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 5, text)
        pdf.ln(2)

    def key_val(key, val):
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(30, 41, 59)
        pdf.write(5, f"  - {key}: ")
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(51, 65, 85)
        pdf.write(5, f"{val}\n")
        pdf.ln(1)

    # 1. Credentials
    section_title('1. DEFAULT PRE-SEEDED CREDENTIALS & ACCESS URLS')
    key_val('Administrator Email', 'admin@researchsphere.ai')
    key_val('Administrator Password', 'Admin@123456')
    key_val('Pre-Seeded Role', 'Administrator (Access to Admin Console, Users Table, Audit Logs)')
    key_val('Single-Click Social Auth', 'Click "Sign in with Google" or "Sign in with GitHub" on Login page')
    key_val('App Web URL', 'http://localhost:5173')
    key_val('Backend Swagger API Docs', 'http://localhost:8000/docs')
    pdf.ln(3)

    # 2. Milestone 1 Checklist Verification
    section_title('2. MILESTONE 1 TASKS & OUTCOMES VERIFICATION (100% COMPLETE)')
    key_val('Define Objectives & Workflows', 'Completed & documented in PROJECT_PLANNING.md + interactive /architecture route')
    key_val('Design Architecture & DB Schema', 'Completed in SYSTEM_ARCHITECTURE.md & DATABASE_DESIGN.md (11 SQL tables + Mongo Cache)')
    key_val('UI Wireframes & Planning', 'Completed in UI_UX_WIREFRAMES.md & Fortune 500 Cobalt Sky React UI')
    key_val('Setup Environments', 'Completed: FastAPI Python 3.11 Backend + React 18 Vite Frontend')
    key_val('Authentication & RBAC', 'Completed: JWT OAuth2 + 4 Personas (Researcher, Founder, Manager, Admin)')
    key_val('Research Profile Workflows', 'Completed: Profile CRUD (/profile) for domains, keywords, citations, and title')
    key_val('Publication & Patent Datasets', 'Completed: OpenAlex, CrossRef, Semantic Scholar, USPTO, Google Patents, The Lens')
    pdf.ln(3)

    # 3. Live Presentation Script
    section_title('3. STEP-BY-STEP LIVE DEMO SCRIPT FOR EVALUATORS (5-7 MINS)')
    sub_title('Step 1: Landing Page & AI Tour Guide (1 Min)')
    body_text('Show http://localhost:5173. Highlight the Fortune 500 cobalt layout, live metric counters (250M+ Papers, 140M+ Patents, $15B+ Grants), and click "AI Platform Tour" in the top header to showcase the interactive onboarding guide modal.')

    sub_title('Step 2: Single-Click Google SSO & Role Dashboard (1 Min)')
    body_text('Open /login. Click "Sign in with Google". Show instant authentication into the Role Dashboard featuring the 4-card metric row, live SVG Citation Growth Velocity chart, and Patent Distribution progress bars.')

    sub_title('Step 3: Multi-Source Publication Search & CSV Export (1.5 Mins)')
    body_text('Open /publications. Search "artificial intelligence". Filter by repository (OpenAlex, CrossRef, Semantic Scholar). Click "Export Results CSV" to download paper citations.')

    sub_title('Step 4: Global Patent Intelligence Explorer (1 Min)')
    body_text('Open /patents. Search "quantum computing". Toggle "Granted Only" status filter. View patent assignees, numbers, and status badges.')

    sub_title('Step 5: Interactive System Architecture & Admin Console (1.5 Mins)')
    body_text('Open /architecture to demonstrate the 4-tier layer explorer & database schema. Open /admin to showcase the User Accounts table, live System Audit Logs, and click "Pre-Seed Platform Datasets". Open /settings to click "Test All Services" database pings.')

    pdf.output(output_path)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == '__main__':
    os.makedirs('docs', exist_ok=True)
    create_pdf('docs/InnovaFund_AI_Milestone1_Final_Showcase_Guide.pdf')
    create_pdf('InnovaFund_AI_Milestone1_Final_Showcase_Guide.pdf')
