function handleSuccess(data) {
    $('#loadingModal').modal('hide');
    
    // Atualiza os links de download
    $('#downloadPptxLink').attr('href', data.arquivo_pptx);
    if (data.arquivo_pdf) {
        $('#downloadPdfLink').attr('href', data.arquivo_pdf);
        $('#downloadPdfLink').show();
    } else {
        $('#downloadPdfLink').hide();
    }
    
    $('#successModal').modal('show');
} 