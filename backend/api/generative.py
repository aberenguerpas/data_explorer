import os
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from utils import load_dataset

class GenerativeEngine:
  def __init__(self, model_name):
    print('Created Generative Engine')
    # Load envs
    os.environ["OPENAI_API_KEY"] =''
    os.environ["GROQ_API_KEY"] =''

    self.model_name = model_name

    if 'gpt' in model_name:
      self.llm = ChatOpenAI(temperature=0, model_name=model_name)
    else:
      self.llm = ChatGroq(temperature=0, model_name=model_name)

  def suggestions(self, item_id, db):
      item_path = '../../datos/'+item_id+'.csv'
      if os.path.exists(item_path):
        try:
            item = db.getItem(item_id)

            title = item['hits'][0]['_source']['title']
         
            parsed = load_dataset(item_id)
            parser = JsonOutputParser()
            format = """[
                    {"titulo":"...", "desc":"..."},
                    {"titulo":"...", "desc":"..."},
                    {"titulo":"...", "desc":"..."}]"""
            template = """
                      Di 4 analísis que se pueda hacer a un dataset cuyo nombre es "{title}"
                      y cuyo contenido sea: {parsed}. Devuelve un json con las 4 ideas. Devuelve únicamente el json
                      El json debe seguir la siguiente estructura: {format}
                      """

            prompt = PromptTemplate(
                template=template,
                input_variables=["title","parsed","format"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )

            chain = prompt | self.llm | parser
            res = chain.invoke({"title": title, "parsed": parsed,
                                "format": format})

            return {"response": res}
        except Exception:
            return {"response": "Error parsing"}
      else:
        return {"response": "Error parsing"}
      
  
  def getKeywords(self, intent):
        intent_template = """
        Te voy a decir una tarea que quiero completar.
        Actúa como experto en analítica de datos.
        Dime hasta 6 consultas que harías a portales de datos que ayuden a resolver la tarea.
        Cada consulta tiene entre 3 y 5 palabras. Cada consulta debe ser única y no deben parecerse entre ellas, en este sentido, los resultados de cada consulta no deberían parecerse.
        
        Además para cada consulta aporta:
        Una Descripción por cada tarea que diga porqué la información que proporciona esa consulta es relevante para resolver la tarea. Tiene que tener entre 10 palabras y 30 palabras.
        Un titulo tiene 3 y 5 palabras.
        
        Además genera una intro generar una intro que indique al usuario porqué esas consultas son útiles para su búsqueda.
        Para la intro no uses más de 60 palabras y qué sea útil y directa. No hagas listas.
        
        Sé realista con las consultas, debe ser información que habitualmente esté disponible y en abierto.
       
        Adicionalmente, como extra, dime portales o APIs dónde se pueda encontrar datasets para la consulta que te voy a pasar.
        Debe estar centrado en España a menos que en la consulta se indique otro lugar.
        Para cada fuente de datos, proporciona un enlace válido para acceder, siendo clikcable el título.
        Por ejemplo si te consultan horarios de trenes. Podrías responder con la siguiente fuente https://data.renfe.com/
        Usa html para maquetar el resultado de lo extra.
        Ejemplo:
        <p><a class='font-semibold underline' href="..." target="_blank">Título de la fuente</a>: Descripción de la fuente...(máximo 20 palabras)<p><br>
        
        La respuesta la debes devolver en formato json. El json debe seguir la siguiente estructura {format}.
        La tarea es la siguiente: {task}.
        """

        parser = JsonOutputParser()

        format = """{intro:"...", "extra":"...", "keywords":[
                {"desc":"...", "titulo":"...", "consulta":"..."},
                {"desc":"...", "titulo":"...", "consulta":"..."},
                {"desc":"...", "titulo":"...", "consulta":"..."}]}"""

        prompt_template = PromptTemplate(
            input_variables=["task"],
            template=intent_template,
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        chain = prompt_template | self.llm | parser
        try:
            res = chain.invoke({"task": intent, "parsed": parser, "format": format})
            return res
        except Exception as e:
            return []


  def additionalInfo(self, query):
    intent_template = """    
    Dime portales o APIs dónde se pueda encontrar datasets para la consulta que te voy a pasar.
    Debe estar centrado en España a menos que en la consulta se indique otro lugar.
    Para cada fuente de datos, proporciona un enlace válido para acceder, siendo clikcable el título.
    Por ejemplo si te consultan horarios de trenes. Podrías responder con la siguiente fuente https://data.renfe.com/
    Usa html para maquetar el resultado.
    Ejemplo:
    <p><a class='font-semibold underline' href="..." target="_blank">Título de la fuente</a>: Descripción de la fuente...(máximo 20 palabras)<p><br>
    Consulta: {query}
    """
    
    prompt_template = PromptTemplate(
        input_variables=["task"],
        template=intent_template
    )
    chain = prompt_template | self.llm
    res = chain.invoke({"query": query})
    return "<p>Addicionalmente existen otras fuentes que pueden ser de utilidad:</p><br>" + res.content

    

  def generateNoResultsResponse(self, query):
    intent_template = """
    Proporciona portales de datos o APIs dónde se pueda encontrar datasets para la consulta que te voy a pasar.
    Tu respuesta debe de ser fiable.
    Los datos deben pertenecer al territorio español o al que se especifíque en la consulta.
    Por favor, para cada fuente de datos proporciona un enlace válido, siendo clickable el título.
    
    Por ejemplo: si te consultan horarios de trenes. Podrías responder con la siguiente fuente https://data.renfe.com/

    Usa html para maquetar el resultado.
    Ejemplo:
    <p><a class='font-semibold underline' href="..." target="_blank">Título de la fuente</a>: Descripción de la fuente...(máximo 20 palabras)<p><br>
    Consulta: {query}
    """
    
    prompt_template = PromptTemplate(
        input_variables=["task"],
        template=intent_template
    )

    chain = prompt_template | self.llm
    res = chain.invoke({"query": query})
    text = "<p class='font-semibold'>Parece que no tenemos en nuestra base de datos la información que buscas, pero no te preocupes, hemos encontrado algo que quizá te sirva:</p><br>"
    return  text+res.content