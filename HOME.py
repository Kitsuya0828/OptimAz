import streamlit as st
from streamlit.logger import get_logger
from streamlit.components.v1 import html

LOGGER = get_logger(__name__)

st.set_page_config(
    page_title="ãã¼ã  | OptimAz",
    page_icon="images/favicon.png"
)

st.image("images/banner_image.png")
st.info("ð ãµã¤ããã¼ããäºä¾ããé¸ãã§ Let's æ°çæé©åï¼")

with st.expander("ð« ã¯ã©ã¹ç·¨æ", expanded=True):
  single_col1, single_col2 = st.columns([2, 1])
  with single_col1:
    st.caption("ãããªãã¨ãèããå¬ç«ä¸­å­¦æ ¡æå¡ã®ã¢ãã¿ã«ï¼")
    st.markdown("""
        * æé©ãªã¯ã©ã¹ç·¨æãããã
        * èªååãã¦æå¡ã®ä½æ¥­ã³ã¹ããåæ¸ããã
        * æè»ã«ã¯ã©ã¹ç·¨æã®ã«ã¼ã«ãå¤æ´ããã
        * ææã«å·¦å³ãããã¯ã©ã¹ç·¨æãããã
    """)
  with single_col2:
    st.image("images/shingakki_classgae.png")

st.markdown("---")

# SNSã·ã§ã¢ãã¿ã³
html("""<a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" data-size="large" data-hashtags="OptimAz" data-url="https://github.com/Kitsuya0828/" data-text="æ°çæé©åWebã¢ããª\n" data-lang="ja" data-show-count="false">Tweet</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
<div class="fb-share-button" data-href="https://github.com/Kitsuya0828/" data-layout="button" data-size="large"><a target="_blank" href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fgithub.com%2FKitsuya0828%2F&amp;src=sdkpreparse" class="fb-xfbml-parse-ignore">ã·ã§ã¢ãã</a></div><div id="fb-root"></div><script async defer crossorigin="anonymous" src="https://connect.facebook.net/ja_JP/sdk.js#xfbml=1&version=v14.0" nonce="yGPVy76g"></script>
<style type="text/css">.fb_iframe_widget > span {vertical-align: baseline !important;}</style>""")