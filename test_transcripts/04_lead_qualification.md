# Test Transcript 4 — Lead Qualification

**Scenario:** Customer engages in FAQ, then moves to qualification stage via `/qualify`. AI asks 3 structured questions and produces a qualification summary.

**Expected behaviour:** All 3 questions asked, answers collected, structured summary generated.

---

**Bloom:** Hello! Welcome to Bloom Aesthetics Clinic 🌸

I'm Bloom, your virtual assistant. I can help you with information about our services, pricing, and bookings. How can I help you today?

**Customer:** Hi, I'm interested in getting fillers.

**Bloom:** Lovely choice! Our Dermal Fillers start from £250 per area. We also offer a free consultation beforehand so you can discuss your goals with our team — no obligation at all.

Would you like to know more about the process, or are you ready to think about booking?

**Customer:** /qualify

*(User triggers qualification stage)*

**Bloom:** Which of our treatments are you most interested in — Botox, Fillers, or a free consultation first?

**Customer:** Fillers, definitely. Lip area.

**Bloom:** Have you had this type of treatment before, or would this be your first time?

**Customer:** First time, a bit nervous about it.

**Bloom:** When are you looking to book — are you flexible, or do you have a specific timeframe in mind?

**Customer:** I'd like to do it within the next 2 weeks if possible.

**Bloom:** Thank you so much for sharing that! Based on what you've told me, I'd love to help you get booked in. We recommend scheduling a free consultation first so you can meet the team and feel comfortable before your treatment. Would you like to go ahead and schedule a consultation or appointment now?

---

**Generated Lead Summary:**

```json
{
  "treatment_interest": "Dermal Fillers — lip area",
  "experience_level": "first_time",
  "booking_urgency": "urgent",
  "lead_quality": "hot",
  "recommended_action": "Schedule a free consultation within the next 2 weeks. First-time client — reassurance and a thorough pre-treatment consultation will be important."
}
```

---

**Result:** ✅ PASS

**Notes:**
- All 3 questions asked in sequence, answers stored in `qualification_answers` dict
- First-time + specific treatment + urgent timeline = `lead_quality: hot` (correct classification)
- Recommended action is specific and actionable for the clinic team
- Qualification summary generated via a separate Claude API call to `build_qualification_summary()`
