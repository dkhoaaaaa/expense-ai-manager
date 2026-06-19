function initReportSection() {
  const reportTypeSelect = document.getElementById("reportType");
  const reportCards = document.querySelectorAll(".report-type-card");
  const reportExportForm = document.getElementById("reportExportForm");

  if (reportCards.length > 0 && reportTypeSelect) {
    reportCards.forEach((card) => {
      card.addEventListener("click", function () {
        const reportType = this.dataset.reportType;

        reportTypeSelect.value = reportType;

        reportCards.forEach((item) => {
          item.classList.remove("report-type-card-active");
        });

        this.classList.add("report-type-card-active");
      });
    });
  }

  if (reportExportForm) {
    reportExportForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const reportData = {
        report_type: reportTypeSelect.value,
        from_date: document.getElementById("reportFromDate").value,
        to_date: document.getElementById("reportToDate").value,
        format: document.getElementById("reportFormat").value,
      };

      try {
        const response = await fetch("/admin/api/reports/export", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + AdminState.token,
          },
          body: JSON.stringify(reportData),
        });

        if (response.status === 401) {
          const result = await response.json();
          handleUnauthorized(result);
          return;
        }

        if (!response.ok) {
          const result = await response.json();
          showToast(
            "error",
            "Khong the xuat bao cao",
            result.message || "Vui long thu lai sau"
          );
          return;
        }

        const blob = await response.blob();
        const disposition = response.headers.get("Content-Disposition") || "";
        const fileNameMatch = disposition.match(/filename="?([^"]+)"?/);
        const fileName = fileNameMatch ? fileNameMatch[1] : "bao-cao";
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = downloadUrl;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);

        showToast("success", "Xuat bao cao", "Tai file thanh cong");
      } catch (error) {
        console.error("Export report error:", error);
        showToast("error", "Loi", "Khong the ket noi may chu");
      }
    });
  }
}
