<template>
  <div class="card">
    <FileUpload
      name="file-uploading"
      url="/api/project/upload-files"
      :customUpload="true"
      @uploader="onUploadClick"
      @upload="onUploadFinished"
      :multiple="true"
      accept="video/*, .yaml, .yml, audio/*"
      :maxFileSize="500 * 1_000_000"
      :fileLimit="100"
    >
      <template #empty>
        <div :style="{ height: 200 + 'px' }">
          <span>Drag and drop files to here to upload.</span>
        </div>
      </template>
    </FileUpload>
  </div>
</template>

<script setup lang="ts">
import FileUpload, {
  type FileUploadUploaderEvent,
  type FileUploadUploadEvent,
} from 'primevue/fileupload'

const emits = defineEmits(['onUpload'])

function onUploadClick(e: FileUploadUploaderEvent) {
  emits('onUpload', e)
}

function onUploadFinished(e: FileUploadUploadEvent) {
  console.log('Upload finished: ', e)
}
</script>
