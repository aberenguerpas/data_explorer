<template>
<main class="md:my-20 mx-4 text-md">
    <button @click="goBack" class="m-12 flex-shrink-0 flex items-center justify-center text-blue-600 w-10 h-10 rounded-full bg-gradient-to-b from-blue-50 to-blue-100 hover:from-white hover:to-blue-50 focus:outline-none focus-visible:from-white focus-visible:to-white transition duration-150 ml-2" >
                                <span class="block font-bold"><span class="sr-only">Read more</span><-</span>
    </button>
<section class="mt-10 max-w-6xl mx-auto md:m-4">
    <div class="text-center mx-auto pb-8">
        <h2 class="text-xl font-semibold text-gray-800">{{ data['title'] }}</h2>
        <p class="text-gray-600 mt-4 text-md md:text-lg">{{ data['description'] }}</p>
        <TableItem/>
        <div v-if="loading" class="m-12">
            <div class="mx-auto w-16 h-16 border-4 border-dashed rounded-full animate-spin border-blue-300"></div>
            <p class="m-4">Cargando muestra</p>
        </div>
    </div>

    <section class="md:grid-cols-2 grid gap-4 mt-10">
        <div class="p-4 bg-white rounded-lg md:basis-1/2">
           <h3 class="font-bold">Metadatos</h3>
           <hr>
           <div class="grid grid-cols-2 gap-4 p-4">
                <div>
                    <h4 class="text-md font-medium">Creado</h4>
                    <span class="pl-2 text-sm">{{ formatdate(data['issued']) }}</span>
                </div>
                <div>
                    <h4 class="text-md font-medium">Última actualización</h4>
                    <span class="pl-2 text-sm">{{ formatdate(data['modified']) }}</span>
                </div>
                <div>
                    <h4 class="text-md font-medium">Cobertura temporal</h4>
                   <span class="pl-2 text-sm">{{ data?.temporal?.startDate ? data?.temporal?.startDate != null: '--'}} - {{ data?.temporal?.endDate ? data?.temporal?.endDate != null : '--'}}</span>
                </div>
                <div>
                    <h4 class="text-md font-medium">Cobertura geográfica</h4>
                    <span class="pl-2 text-sm">{{ data['geo']!=null ? data['geo'] : '--' }}</span>

                </div>
                <div class="truncate">
                    <h4 class="text-md font-medium">Licencia</h4>
                    <a class="pl-2 text-sm" :href="data['license']">{{ data['license']!=null ? data['license'] : '--'  }}</a>
                </div>
                <div>
                    <h4 class="text-md font-medium">Fuente</h4>
                    <a class="pl-2 text-sm" href="https://datos.gob.es">https://datos.gob.es</a>
                </div>
            </div>
        </div>

        <div class="p-4 bg-white rounded-lg md:basis-1/2">
           <h3 class="font-bold">Recursos</h3>
           <hr>
           <div class=" max-h-[200px] overflow-auto">
                <div v-for="i in data['resources'] ">
                    <ResourceItem :data="i" class="m-3"/>
                </div>
            </div>
        </div>
    </section>

    <section class="text-center mt-20 mb-8">
        <h3 class="text-xl font-semibold text-gray-800 mb-8">También te podría interesar...</h3>
        <div v-for="i in similars">
            <ResultItem :data="i" class="mt-2"/>
        </div>
    </section>
    <!--
    <section v-if="!existeIdeas && existDataset" class="mt-20 text-center">
        <div class="flex flex-row justify-center items-center pr-16">
            <svg class="m-4" width="50px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M7.45284 2.71266C7.8276 1.76244 9.1724 1.76245 9.54716 2.71267L10.7085 5.65732C10.8229 5.94743 11.0526 6.17707 11.3427 6.29148L14.2873 7.45284C15.2376 7.8276 15.2376 9.1724 14.2873 9.54716L11.3427 10.7085C11.0526 10.8229 10.8229 11.0526 10.7085 11.3427L9.54716 14.2873C9.1724 15.2376 7.8276 15.2376 7.45284 14.2873L6.29148 11.3427C6.17707 11.0526 5.94743 10.8229 5.65732 10.7085L2.71266 9.54716C1.76244 9.1724 1.76245 7.8276 2.71267 7.45284L5.65732 6.29148C5.94743 6.17707 6.17707 5.94743 6.29148 5.65732L7.45284 2.71266Z" fill="#a5b4fc"></path> <path d="M16.9245 13.3916C17.1305 12.8695 17.8695 12.8695 18.0755 13.3916L18.9761 15.6753C19.039 15.8348 19.1652 15.961 19.3247 16.0239L21.6084 16.9245C22.1305 17.1305 22.1305 17.8695 21.6084 18.0755L19.3247 18.9761C19.1652 19.039 19.039 19.1652 18.9761 19.3247L18.0755 21.6084C17.8695 22.1305 17.1305 22.1305 16.9245 21.6084L16.0239 19.3247C15.961 19.1652 15.8348 19.039 15.6753 18.9761L13.3916 18.0755C12.8695 17.8695 12.8695 17.1305 13.3916 16.9245L15.6753 16.0239C15.8348 15.961 15.961 15.8348 16.0239 15.6753L16.9245 13.3916Z" fill="#a5b4fc"></path> </g></svg>
            <h3 class="text-xl font-semibold text-gray-800">Inspírate</h3>
        </div>
        <p class="md:w-1/2 mx-auto text-center italic">Sabemos que es difícil trabajar con datos, por eso te ofrecemos algunas ideas por las que podrías empezar</p>

        <button v-if="!generandoIdeas && existDataset" type="button" class="m-8 text-white bg-gradient-to-br from-purple-600 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center" @click="getSuggestions">Generar ideas</button>

        <div class="flex flex-row flex-wrap m-4">
            <div v-if="generandoIdeas && suggestions.length==0" class="m-8 w-full text-center">
                <div class="mx-auto w-16 h-16 border-4 border-dashed rounded-full animate-spin border-blue-300"></div>
                <p class="p-4">Preparando ideas...</p>
            </div>
                <div class="md:basis-1/2 text-left p-4" v-for="i in suggestions">
                        <h4 class="text-lg font-semibold">{{i['titulo']}}</h4>
                        <div>{{i['desc']}}</div>
                </div>
        </div>
    </section>
    -->
</section>
</main>
</template>

<script setup>
import ResourceItem from '@/components/ResourceItem.vue';
import ResultItem from '@/components/ResultItem.vue';
import TableItem from '@/components/TableItem.vue';
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router';

import { onMounted } from 'vue';
import { ref, watch } from 'vue';

const data = ref('')
const similars = ref('')
const route = useRoute()
const suggestions = ref('')
const loading = ref(true)
const existDataset = ref(false)
const existeIdeas = ref(false)
const generandoIdeas = ref(false)
const router = useRouter()

const createTableFromJson = (json) => {
        let table = document.createElement('table');
        table.classList.add("w-full", "text-sm", "text-left", "text-gray-500", "dark:text-gray-400")
        let tbody = document.createElement('tbody');
        let thead = document.createElement('thead');
        thead.classList.add("text-xs", "text-gray-700", "uppercase", "bg-gray-50", "dark:bg-gray-700", "dark:text-gray-400");
        // Add column headers
        let headerRow = document.createElement('tr');
        
        Object.keys(json[Object.keys(json)[0]]).forEach(headerText => {
            let header = document.createElement('th');
            header.classList.add("py-3", "px-6");
            let textNode = document.createTextNode(headerText);
            header.appendChild(textNode);
            headerRow.appendChild(header);
        });
        thead.appendChild(headerRow);

        // Add rows
        Object.values(json).slice(0, 10).forEach(rowData => {
            let row = document.createElement('tr');
            row.classList.add("bg-white", "border-b", "dark:bg-gray-800", "dark:border-gray-700")
            Object.values(rowData).forEach(cellData => {
                let cell = document.createElement('td');
                cell.classList.add("py-3", "px-6", "truncate");
                let cellTextNode = document.createTextNode(cellData);
                cell.appendChild(cellTextNode);
                row.appendChild(cell);
            });
            tbody.appendChild(row);
        });

        table.appendChild(thead);
        table.appendChild(tbody);
        document.getElementById('table-container').appendChild(table);
    }

const getSample = async ()=>{
    loading.value = true;
    existDataset.value = false
    const id = route.params.datasetId
    try{
        const res = await fetch('http://127.0.0.1:8000/dataset/'+id+'/sample')
        const jsonResponse = await res.json()

        if(jsonResponse['response']!="Error al recuperar contenido"){
            existDataset.value = true
            createTableFromJson(jsonResponse['response'])
        }else{
            existDataset.value = false
        }
    }catch(error){
        //console.log(error)
        loading.value = false;
        //existDataset.value = false
    }finally{

        loading.value = false; // Deactivate the loading spinner
    }
}

const getRelateds = async (text)=>{
    const res = await fetch('http://127.0.0.1:8000/similar?q='+text)
    const jsonResponse = await res.json()
    similars.value = jsonResponse['hits']
}

const getSuggestions = async ()=>{
    const id = route.params.datasetId
    generandoIdeas.value = true
    try{
        existeIdeas.value = false
        const res = await fetch('http://127.0.0.1:8000/dataset/'+id+'/suggestions')
        const jsonResponse = await res.json()

        if(jsonResponse['response']!="Error parsing"){
            existeIdeas.value = false
            suggestions.value = jsonResponse['response']

        }else{
            existeIdeas.value = true
        }

    }catch(error){
        //console.error("Error fetching data: ", error);
    }
}

onMounted(async () => {
    const id = route.params.datasetId
    const res = await fetch('http://127.0.0.1:8000/dataset/'+id)
    const jsonResponse = await res.json()
    data.value = jsonResponse
    getRelateds(jsonResponse['title'])
    getSample()
})

watch(route,  async() => {
    const id = route.params.datasetId
    const res = await fetch('http://127.0.0.1:8000/dataset/'+id)
    const jsonResponse = await res.json()
    data.value = jsonResponse
    getRelateds(jsonResponse['title'])
    getSample()
})

const goBack = ()=>{
    router.go(-1)
}

const formatdate = (dateStr)=>{

    if(dateStr!=null){
        
        // Remove the day-of-week prefix
        const cleanedDateStr = dateStr.substring(dateStr.indexOf(',') + 1).trim();

        // Parse the cleaned string into a Date object
        const months = {
        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06',
        'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
        };

        // Split the date string and extract the relevant parts
        const parts = cleanedDateStr.split(' ');
        const day = parts[0];
        const month = months[parts[1].toLowerCase()];
        const year = parts[2].substring(2);

        // Construct the new date format
        return `${day}/${month}/${year}`;
    }else{
        return '--';
    }
}


</script>