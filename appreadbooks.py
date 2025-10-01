import streamlit as st

def run():
    st.markdown("<h1 style='text-align:center; color:white;'>📘 The Silly Brain Tricks — Simple Story</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;'>
        <p style='font-size:20px;'>🧠 Once upon a time, there was a little brain. It worked very hard every day — thinking, deciding, and helping its human.</p>
        <p style='font-size:20px;'>But this brain had a problem… it sometimes played <b>silly tricks</b> on itself!</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/4287/4287720.png", width=200)
        st.markdown("### 👀 Swimmer Trick")
        st.write("The brain saw a strong swimmer and thought, 'If I swim, I’ll look like that!' But no — swimmers look that way because they were already strong.")

        st.image("https://cdn-icons-png.flaticon.com/512/620/620851.png", width=200)
        st.markdown("### 🏆 Winner Trick")
        st.write("The brain saw a rich person and said, 'I can do that too!' but forgot about the many who failed. That’s the Winner Trick!")

        st.image("https://cdn-icons-png.flaticon.com/512/4341/4341139.png", width=200)
        st.markdown("### 👥 Crowd Trick")
        st.write("The brain saw people running and followed them without knowing why. That’s the Crowd Trick!")

    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3199/3199875.png", width=200)
        st.markdown("### 💰 Sunk Cost Trick")
        st.write("The brain bought a toy that broke but kept it because it spent money. That’s the Sunk Cost Trick!")

        st.image("https://cdn-icons-png.flaticon.com/512/5893/5893552.png", width=200)
        st.markdown("### 🎁 Give-Back Trick")
        st.write("Someone gave the brain candy, so it gave candy back even when it didn’t want to. That’s the Give-Back Trick!")

        st.image("https://cdn-icons-png.flaticon.com/512/5787/5787211.png", width=200)
        st.markdown("### 🎩 Boss Trick")
        st.write("The brain believed someone just because he wore a suit. That’s the Boss Trick!")

    st.markdown("---")

    st.markdown("""
    <div style='text-align:center;'>
        <img src='https://cdn-icons-png.flaticon.com/512/3285/3285558.png' width='200'>
        <h3>🦉 The Wise Owl said:</h3>
        <p style='font-size:20px;'>“Dear little brain, you make tiny thinking mistakes every day. Learn about your tricks — and you will think clearly like a calm lake on a sunny day.”</p>
        <p style='font-size:22px; color:lightyellow;'>🌞 The little brain smiled and said, “I’ll watch out for my silly tricks!”</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style='text-align:center; background:rgba(255,255,255,0.1); padding:20px; border-radius:15px;'>
        <h3>🌟 Conclusion</h3>
        <p style='font-size:20px;'>
        This story teaches us that our brain is very smart but sometimes it makes funny mistakes.  
        When we know these mistakes, we can stop and think better.  
        So next time, when your brain says something too quickly — pause, smile, and ask,  
        “Is this a trick?” 😄  
        That way, we can make smart choices and be happy, clear thinkers every day.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ✅ New Section: Short Book Summaries on Critical Thinking
    st.markdown("<h2 style='text-align:center; color:white;'>📚 More Fun Books About Smart Thinking</h2>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:15px; margin-top:20px;'>
        <h3>📖 1. “Thinking, Fast and Slow” — Daniel Kahneman</h3>
        <p style='font-size:18px;'>
        This book says our brain has two helpers: one is <b>Fast</b> (quick and lazy), and one is <b>Slow</b> (careful and smart).  
        The Fast helper makes quick guesses — sometimes wrong!  
        The Slow one takes time and finds truth.  
        The lesson: Don’t rush — think slow and check your thoughts. 🐢💭
        </p>
    </div>

    <div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:15px; margin-top:20px;'>
        <h3>📘 2. “The Art of Thinking Clearly” — Rolf Dobelli</h3>
        <p style='font-size:18px;'>
        This book shows many small mistakes our brain makes — like following the crowd or copying others.  
        It helps us spot those mistakes and say, “Wait! I’ll decide for myself.” ✋  
        The lesson: Look carefully before believing or acting.
        </p>
    </div>

    <div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:15px; margin-top:20px;'>
        <h3>📙 3. “Predictably Irrational” — Dan Ariely</h3>
        <p style='font-size:18px;'>
        This book says people think they are smart — but often do funny things! 😂  
        We choose things because of feelings, not facts.  
        The lesson: Know your feelings, check your thoughts, and make fair, clear choices.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; margin-top:40px;'>
        <img src='https://cdn-icons-png.flaticon.com/512/3267/3267888.png' width='150'>
        <h3 style='color:lightyellow;'>💡 Be a Smart Thinker!</h3>
        <p style='font-size:20px;'>Every big idea starts with a small, careful thought. 🌱</p>
    </div>
    """, unsafe_allow_html=True)
