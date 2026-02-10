"""
Client Proposals Page - TikTik Smart Order System
עמוד הצעות מחיר ללקוחות
"""

import streamlit as st
from datetime import datetime
from models import ClientProposal, ProposalStatus, get_db


def page_proposals():
    """Page for managing client proposals"""
    st.markdown("""
    <div class="header-container">
        <h1>💼 הצעות ללקוח</h1>
        <p>ניהול הצעות מחיר ללקוחות</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ חזרה לתפריט"):
        st.session_state.admin_page = None
        st.rerun()
    
    st.markdown("---")
    
    st.info("💡 **ליצור הצעה חדשה:** מלא את טופס ההזמנה הרגיל ולחץ על '💼 שמור כהצעה ללקוח'.")
    
    st.markdown("### 📋 הצעות שמורות")
    
    from models import ClientProposal, ProposalStatus
    
    db = get_db()
    proposals = []
    if db:
        try:
            proposals = db.query(ClientProposal).filter(ClientProposal.is_active == True).order_by(ClientProposal.created_at.desc()).all()
        except Exception as e:
            st.error(f"❌ שגיאה בטעינת הצעות: {e}")
        finally:
            db.close()
    
    if not proposals:
        st.info("💼 אין הצעות שמורות. לך להזמנה חדשה ושמור הצעה משם.")
    else:
        st.markdown(f"**סה\"כ: {len(proposals)} הצעות**")
        
        # Status filter
        status_filter = st.multiselect(
            "סנן לפי סטטוס",
            ["draft", "sent", "accepted", "rejected"],
            default=["draft", "sent"],
            format_func=lambda x: {"draft": "טיוטה", "sent": "נשלח", "accepted": "אושר", "rejected": "נדחה"}[x]
        )
        
        filtered_proposals = [p for p in proposals if p.status.value in status_filter] if status_filter else proposals
        
        for proposal in filtered_proposals:
            prop_dict = proposal.to_dict()
            with st.container():
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([4, 2, 2])
                
                with col1:
                    st.markdown(f"### 💼 {prop_dict.get('name', 'הצעה')}")
                    st.markdown(f"👤 **לקוח:** {prop_dict.get('customer_name', '')}")
                    if prop_dict.get('customer_email'):
                        st.caption(f"📧 {prop_dict.get('customer_email')}")
                    if prop_dict.get('customer_phone'):
                        st.caption(f"📱 {prop_dict.get('customer_phone')}")
                
                with col2:
                    created = prop_dict.get('created_at', '')
                    if created:
                        st.markdown(f"📅 {created[:10]}")
                    if prop_dict.get('total_price_euro'):
                        st.markdown(f"💶 {prop_dict.get('total_price_euro'):.0f}€")
                    if prop_dict.get('total_price_nis'):
                        st.markdown(f"💰 {prop_dict.get('total_price_nis'):,.0f}₪")
                    
                    # Status badge
                    status_colors = {
                        'draft': ('#6c757d', 'טיוטה'),
                        'sent': ('#007bff', 'נשלח'),
                        'accepted': ('#28a745', 'אושר'),
                        'rejected': ('#dc3545', 'נדחה')
                    }
                    color, label = status_colors.get(prop_dict.get('status', 'draft'), ('#6c757d', 'טיוטה'))
                    st.markdown(f'<span style="background: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem;">{label}</span>', unsafe_allow_html=True)
                
                with col3:
                    # Action buttons
                    if st.button("✏️ ערוך", key=f"edit_prop_{proposal.id}", use_container_width=True):
                        # Load proposal data back to form
                        data = prop_dict.get('data', {})
                        st.session_state.admin_page = None
                        st.session_state['load_proposal_data'] = data
                        st.rerun()
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("📋", key=f"dup_prop_{proposal.id}", help="שכפל", use_container_width=True):
                            dup_db = get_db()
                            if dup_db:
                                try:
                                    import json
                                    new_prop = ClientProposal(
                                        proposal_name=f"{proposal.proposal_name} (עותק)",
                                        customer_name=proposal.customer_name,
                                        customer_email=proposal.customer_email,
                                        customer_phone=proposal.customer_phone,
                                        proposal_data=proposal.proposal_data,
                                        total_price_euro=proposal.total_price_euro,
                                        total_price_nis=proposal.total_price_nis,
                                        status=ProposalStatus.DRAFT
                                    )
                                    dup_db.add(new_prop)
                                    dup_db.commit()
                                    st.success("✅ ההצעה שוכפלה!")
                                    st.rerun()
                                except Exception as e:
                                    dup_db.rollback()
                                    st.error(f"❌ {e}")
                                finally:
                                    dup_db.close()
                    with col_b:
                        if st.button("🗑️", key=f"del_prop_{proposal.id}", help="מחק", use_container_width=True):
                            del_db = get_db()
                            if del_db:
                                try:
                                    del_db.query(ClientProposal).filter(ClientProposal.id == proposal.id).update({'is_active': False})
                                    del_db.commit()
                                    st.success("✅ ההצעה נמחקה!")
                                    st.rerun()
                                except:
                                    del_db.rollback()
                                finally:
                                    del_db.close()
                
                with st.expander("📄 פרטים מלאים"):
                    data = prop_dict.get('data', {})
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**פרטי אירוע:**")
                        if data.get('event_name'):
                            st.write(f"- אירוע: {data.get('event_name')}")
                        if data.get('event_date'):
                            st.write(f"- תאריך: {data.get('event_date')}")
                        if data.get('venue'):
                            st.write(f"- מקום: {data.get('venue')}")
                        if data.get('category'):
                            st.write(f"- קטגוריה: {data.get('category')}")
                        
                        saved_games = data.get('saved_games', [])
                        if saved_games:
                            st.markdown("**אירועים נוספים:**")
                            for idx, game in enumerate(saved_games):
                                st.write(f"  {idx+1}. {game.get('display_text', '')}")
                    
                    with col2:
                        st.markdown("**פרטי לקוח:**")
                        if data.get('customer_name'):
                            st.write(f"- שם: {data.get('customer_name')}")
                        if data.get('customer_email'):
                            st.write(f"- אימייל: {data.get('customer_email')}")
                        if data.get('customer_phone'):
                            st.write(f"- טלפון: {data.get('customer_phone')}")
                        
                        st.markdown("**נוסעים:**")
                        passengers = data.get('passengers', [])
                        if isinstance(passengers, str):
                            try:
                                import json
                                passengers = json.loads(passengers)
                            except:
                                passengers = []
                        st.write(f"- מספר: {len(passengers) if passengers else 0}")
                    
                    # Status update buttons
                    st.markdown("---")
                    st.markdown("**עדכון סטטוס:**")
                    col_s1, col_s2, col_s3 = st.columns(3)
                    with col_s1:
                        if st.button("📤 נשלח", key=f"sent_prop_{proposal.id}", use_container_width=True):
                            upd_db = get_db()
                            if upd_db:
                                try:
                                    upd_db.query(ClientProposal).filter(ClientProposal.id == proposal.id).update({
                                        'status': ProposalStatus.SENT,
                                        'sent_at': datetime.utcnow()
                                    })
                                    upd_db.commit()
                                    st.success("✅ סטטוס עודכן!")
                                    st.rerun()
                                except:
                                    upd_db.rollback()
                                finally:
                                    upd_db.close()
                    with col_s2:
                        if st.button("✅ אושר", key=f"accept_prop_{proposal.id}", use_container_width=True):
                            upd_db = get_db()
                            if upd_db:
                                try:
                                    upd_db.query(ClientProposal).filter(ClientProposal.id == proposal.id).update({'status': ProposalStatus.ACCEPTED})
                                    upd_db.commit()
                                    st.success("✅ סטטוס עודכן!")
                                    st.rerun()
                                except:
                                    upd_db.rollback()
                                finally:
                                    upd_db.close()
                    with col_s3:
                        if st.button("❌ נדחה", key=f"reject_prop_{proposal.id}", use_container_width=True):
                            upd_db = get_db()
                            if upd_db:
                                try:
                                    upd_db.query(ClientProposal).filter(ClientProposal.id == proposal.id).update({'status': ProposalStatus.REJECTED})
                                    upd_db.commit()
                                    st.success("✅ סטטוס עודכן!")
                                    st.rerun()
                                except:
                                    upd_db.rollback()
                                finally:
                                    upd_db.close()
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("")


