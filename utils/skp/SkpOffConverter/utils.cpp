#include "utils.h"

#include <SketchUpAPI/import_export/pluginprogresscallback.h>

bool IsCancelled(SketchUpPluginProgressCallback* callback) {
  return callback != NULL && callback->HasBeenCancelled();
}

void HandleProgress(SketchUpPluginProgressCallback* callback,
  double percent_done, const char* message) {
  if (callback != NULL) {
    if (callback->HasBeenCancelled()) {
      // Throw an exception to be caught by the top-level handler.
      throw std::exception();
    }
    else {
      callback->SetPercentDone(percent_done);
      callback->SetProgressMessage(message);
    }
  }
}