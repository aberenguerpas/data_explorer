<template>
  <div class="border-solid border-2 border-stone-100 rounded-lg my-2 cursor-pointer hover:bg-stone-100" @click="download(props.data.downloadUrl)">
    <div class="flex flex-row py-2 text-sm items-center text-center">
      <span class="ml-2 inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-600 ring-1 ring-inset ring-blue-500/10">{{ formatDtype(props.data.mediaType) }}</span>
      <div class="basis-3/4 mx-2 line-clamp-3">{{props.data.name}}</div>
      <div class="basis-1/4 mx-2 font-medium text-sm">{{props.data.size!=null ? formatBytes(props.data.size) : '--'}}</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps(['data'])

const formatBytes = (bytes, decimals = 2)=> {

bytes = bytes.toString().replace(/\./g,'');
if (bytes === 0) return '0 Bytes';

const k = 1024;
const dm = decimals < 0 ? 0 : decimals;
const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

const i = Math.floor(Math.log(bytes) / Math.log(k));

return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

const download = (url) =>{
  const link = document.createElement('a');
  link.href = url;
  link.target = "_blank";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  }

const formatDtype = (type)=>{
  type = type.toLowerCase();

  if (type.includes("csv")){
    return 'CSV'
  }

  if (type.includes("html")){
    return 'HTML'
  }

  if (type.includes("json")){
    return 'JSON'
  }

  if (type.includes("excel") || type.includes("xls")|| type.includes("xlsx")){
    return 'Excel'
  }

  return 'Otro'
}
</script>