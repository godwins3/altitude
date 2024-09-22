from server import pipe

def translate_lang(string, src_lang, tgt_lang):

    response = pipe(string, src_lang=src_lang, tgt_lang=tgt_lang)
    
    return response