# OrganicScale AI: Winning MVP Plan
**CWA PROMPT-A-THON 2026**
**Theme**: AI for Startups (Solo/Early-Stage)
**Twist**: Human-in-the-loop (HIL)

## 1. Problem & Solution
- **Problem**: Solo founders have live products but $0 for ads. They need to post daily on socials but lack time/inspiration.
- **Solution**: An AI engine that scans their URL/Product Info, drafts viral-potential social posts, and **requires human "Personalization"** before the post is finalized and scheduled.

## 2. Key Features (Winning MVP)
| Feature | Description | Points |
| :--- | :--- | :--- |
| **Product Scanner** | Input URL + Description. AI identifies core "Hooks" for the product. | Completeness (3) |
| **HIL Review Lab** | **THE TWIST**: AI generates 3 drafts (Twitter, LinkedIn, IG). The "Finalize" button is locked until the user edits or adds a "Founder's Voice" nugget. | Twist (3) |
| **Content Vault** | Save finalized posts locally. | Completeness (3) |
| **Direct Post/Share** | Integration with Flutter `share_plus` to post directly to social apps. | Usability (2) |
| **Engagement Notify** | Local notifications to remind the founder: "Your post is ready for the human touch!" | Bonus (UX) |

## 3. Premium UI/UX Design
- **Theme**: Dark Mode "Founder Blue" & "Neon Mint" accents.
- **Aesthetic**: Glassmorphism cards for the draft posts.
- **Feedback**: Shimmer effects while AI "scans" the product website.

## 4. Tech Stack (Speed-First)
- **Frontend**: Flutter.
- **AI**: Gemini 3 Flash Preview (`firebase_ai`) for scraping-like analysis & drafting.
- **Storage**: `hive` or `shared_preferences` (fast for MVP). 
- **Utilities**: `share_plus` (for posting), `url_launcher` (for links).

## 5. Implementation Roadmap (Today)
- **12:00 PM - 1:15 PM**: Build the **Product Intake & Scanning UI**.
- **1:15 PM - 2:30 PM**: Integrate Gemini Prompting for "Product Context" -> Social Drafts.
- **2:30 PM - 3:30 PM**: **THE TWIST**: Build the "Human Refinement" screen (Side-by-side AI vs. Human Edit).
- **3:30 PM - 4:30 PM**: Notifications, "Share" integration, and UI Polish.
- **4:30 PM - 5:00 PM**: **Record 2-minute video focusing on the HIL "Review Lab".**
