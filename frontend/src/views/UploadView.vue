<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-foreground mb-2">
        Upload HOS Audit Files
      </h1>
      <p class="text-muted-foreground text-lg">
        Upload ELD logs, fuel receipts, and BOLs for FMCSA Hours-of-Service
        compliance auditing
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Upload Form -->
      <Card class="bg-card/50 backdrop-blur-sm border-border/50">
        <CardHeader>
          <h2 class="text-xl font-bold text-foreground">Upload Documents</h2>
          <p class="text-sm text-muted-foreground">
            Upload driver logs and supporting documentation
          </p>
        </CardHeader>
        <CardContent>
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <!-- Driver Information -->
            <div>
              <Label
                for="driverName"
                class="text-sm font-medium text-foreground"
                >Driver Name</Label
              >
              <Input
                id="driverName"
                v-model="formData.driverName"
                type="text"
                required
                placeholder="Enter driver name"
                class="mt-1"
              />
            </div>

            <!-- Driver Type Selection -->
            <div>
              <Label
                for="driverType"
                class="text-sm font-medium text-foreground"
                >Driver Type</Label
              >
              <Select
                id="driverType"
                v-model="formData.driverType"
                required
                class="mt-1"
              >
                <option value="">Select driver type</option>
                <option value="long-haul">
                  Long Haul (Beyond 150 air miles)
                </option>
                <option value="short-haul">
                  Short Haul (Within 150 air miles)
                </option>
                <option value="exemption">
                  Exemption (Special certificates)
                </option>
              </Select>
            </div>

            <!-- File Upload -->
            <div>
              <Label class="text-sm font-medium text-foreground"
                >Upload Files</Label
              >
              <div
                @drop.prevent="handleDrop"
                @dragover.prevent
                @dragenter.prevent
                class="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors mt-1"
                :class="{ 'border-primary/50 bg-primary/5': isDragOver }"
              >
                <UploadIcon
                  class="mx-auto h-12 w-12 text-muted-foreground mb-4"
                />
                <div class="mt-4">
                  <Button
                    type="button"
                    variant="outline"
                    @click="$refs.fileInput.click()"
                    class="rounded-lg"
                  >
                    Select Files
                  </Button>
                  <p class="mt-3 text-sm text-muted-foreground">
                    Drag and drop or click to upload ELD logs, fuel receipts,
                    and BOLs
                  </p>
                  <p class="mt-1 text-xs text-muted-foreground">
                    Supported: PDF, JPEG, PNG, Excel files
                  </p>
                </div>
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls"
                  @change="handleFileSelect"
                  class="hidden"
                />
              </div>
            </div>

            <!-- File List -->
            <div v-if="selectedFiles.length > 0">
              <Label class="text-sm font-medium text-foreground"
                >Selected Files</Label
              >
              <div class="space-y-2 mt-1">
                <div
                  v-for="(file, index) in selectedFiles"
                  :key="index"
                  class="flex items-center justify-between p-3 bg-muted/30 rounded-lg border border-border/50"
                >
                  <div class="flex items-center">
                    <DocumentIcon class="w-5 h-5 text-muted-foreground mr-3" />
                    <div>
                      <span class="text-sm font-medium text-foreground">{{
                        file.name
                      }}</span>
                      <span class="ml-2 text-xs text-muted-foreground"
                        >({{ formatFileSize(file.size) }})</span
                      >
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    @click="removeFile(index)"
                    class="text-destructive hover:text-destructive/80 rounded-lg"
                  >
                    <XIcon class="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            <!-- Submit Button -->
            <div class="flex justify-end pt-4">
              <Button
                type="submit"
                :disabled="isSubmitting || selectedFiles.length === 0"
                size="lg"
                class="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-lg rounded-lg"
              >
                <RefreshIcon
                  v-if="isSubmitting"
                  class="animate-spin -ml-1 mr-3 h-5 w-5"
                />
                {{
                  isSubmitting ? "Processing HOS Audit..." : "Start FMCSA Audit"
                }}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <!-- Instructions -->
      <div class="space-y-6">
        <Card
          class="bg-gradient-to-br from-blue-500/5 to-blue-600/10 border-blue-200/30"
        >
          <CardHeader>
            <h3 class="text-lg font-bold text-foreground">
              Required Documents
            </h3>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div class="flex items-start">
                <div
                  class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3 mt-0.5"
                >
                  <DocumentIcon class="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <h4 class="font-medium text-foreground">
                    ELD Driver Logs (PDF)
                  </h4>
                  <p class="text-sm text-muted-foreground mt-1">
                    Electronic logging device records for the audit period
                  </p>
                </div>
              </div>
              <div class="flex items-start">
                <div
                  class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-0.5"
                >
                  <DocumentIcon class="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <h4 class="font-medium text-foreground">
                    Fuel Receipts (JPEG/PDF)
                  </h4>
                  <p class="text-sm text-muted-foreground mt-1">
                    Fuel purchase receipts to verify duty status accuracy
                  </p>
                </div>
              </div>
              <div class="flex items-start">
                <div
                  class="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center mr-3 mt-0.5"
                >
                  <DocumentIcon class="w-4 h-4 text-amber-600" />
                </div>
                <div>
                  <h4 class="font-medium text-foreground">
                    Bills of Lading (JPEG/PDF)
                  </h4>
                  <p class="text-sm text-muted-foreground mt-1">
                    Shipping documents to verify cargo and route information
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          class="bg-gradient-to-br from-green-500/5 to-green-600/10 border-green-200/30"
        >
          <CardHeader>
            <h3 class="text-lg font-bold text-foreground">
              FMCSA Compliance Rules
            </h3>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div>
                <h4 class="font-medium text-foreground mb-2">
                  Hours-of-Service (HOS) Violations
                </h4>
                <ul class="text-sm text-muted-foreground space-y-1">
                  <li>
                    • Driving beyond 14 consecutive hours after 10 consecutive
                    hours off duty
                  </li>
                  <li>• Exceeding 60/70 hour limits in 7/8 day windows</li>
                  <li>• No record of duty status for logged time</li>
                </ul>
              </div>
              <div>
                <h4 class="font-medium text-foreground mb-2">
                  Other Violations
                </h4>
                <ul class="text-sm text-muted-foreground space-y-1">
                  <li>• Log falsification and form/manner violations</li>
                  <li>• Driving while marked off duty</li>
                  <li>• Fueling while off duty</li>
                  <li>• Implausible behavior (geographic inconsistencies)</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          class="bg-gradient-to-br from-amber-500/5 to-amber-600/10 border-amber-200/30"
        >
          <CardHeader>
            <h3 class="text-lg font-bold text-foreground">
              Processing Information
            </h3>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div class="flex items-start">
                <InfoIcon class="w-5 h-5 text-amber-600 mr-3 mt-0.5" />
                <div>
                  <p class="text-sm text-foreground font-medium">
                    AI-Powered Analysis
                  </p>
                  <p class="text-sm text-muted-foreground mt-1">
                    Documents are processed using advanced AI for FMCSA
                    compliance detection
                  </p>
                </div>
              </div>
              <div class="flex items-start">
                <InfoIcon class="w-5 h-5 text-amber-600 mr-3 mt-0.5" />
                <div>
                  <p class="text-sm text-foreground font-medium">
                    Driver Type Specific
                  </p>
                  <p class="text-sm text-muted-foreground mt-1">
                    Audit logic adapts based on driver classification and
                    exemptions
                  </p>
                </div>
              </div>
              <div class="flex items-start">
                <InfoIcon class="w-5 h-5 text-amber-600 mr-3 mt-0.5" />
                <div>
                  <p class="text-sm text-foreground font-medium">
                    Exportable Reports
                  </p>
                  <p class="text-sm text-muted-foreground mt-1">
                    Detailed CSV/Excel reports with violation analysis and
                    compliance scores
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuditStore } from "../stores/audit";
import Button from "@/components/ui/button.vue";
import Input from "@/components/ui/input.vue";
import Label from "@/components/ui/label.vue";
import Select from "@/components/ui/select.vue";
import Card from "@/components/ui/card.vue";
import CardHeader from "@/components/ui/card-header.vue";
import CardContent from "@/components/ui/card-content.vue";
import {
  UploadIcon,
  DocumentIcon,
  XIcon,
  RefreshIcon,
  InfoIcon,
} from "@/assets/icons";

const router = useRouter();
const auditStore = useAuditStore();

const formData = reactive({
  driverName: "",
  driverType: "",
});

const selectedFiles = ref([]);
const isDragOver = ref(false);
const isSubmitting = ref(false);

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files);
  addFiles(files);
};

const handleDrop = (event) => {
  isDragOver.value = false;
  const files = Array.from(event.dataTransfer.files);
  addFiles(files);
};

const addFiles = (files) => {
  const validTypes = [
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
  ];

  files.forEach((file) => {
    if (validTypes.includes(file.type)) {
      selectedFiles.value.push(file);
    }
  });
};

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1);
};

const formatFileSize = (bytes) => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const handleSubmit = async () => {
  if (selectedFiles.value.length === 0) return;

  isSubmitting.value = true;

  try {
    // Step 1: Create audit
    const auditData = {
      driverName: formData.driverName,
      driverType: formData.driverType,
    };

    const newAudit = await auditStore.createAudit(auditData);

    // Step 2: Upload files
    await auditStore.uploadFiles(newAudit.id, selectedFiles.value);

    // Step 3: Process audit
    await auditStore.processAudit(newAudit.id);

    router.push(`/audit/${newAudit.id}`);
  } catch (error) {
    console.error("Error creating audit:", error);
    // You might want to show an error message to the user here
  } finally {
    isSubmitting.value = false;
  }
};
</script>
