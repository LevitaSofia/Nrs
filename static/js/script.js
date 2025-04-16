function showSuccessModal(pptxPath, pdfPath) {
    const pptxLink = document.getElementById('downloadPptxLink');
    const pdfLink = document.getElementById('downloadPdfLink');
    
    if (pptxPath) {
        pptxLink.href = pptxPath;
        pptxLink.style.display = 'inline-flex';
    }
    
    if (pdfPath) {
        pdfLink.href = pdfPath;
        pdfLink.style.display = 'inline-flex';
    }
    
    const successModal = new bootstrap.Modal(document.getElementById('successModal'));
    successModal.show();
}

function showErrorModal(message) {
    const errorMessageElement = document.getElementById('errorMessage');
    if (errorMessageElement) {
        errorMessageElement.textContent = message;
    }
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    errorModal.show();
}

function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData();
    const collaborator = document.getElementById('collaborator');
    const selectedOption = collaborator.options[collaborator.selectedIndex];
    const selectedNRs = Array.from(document.querySelectorAll('input[name="nrs"]:checked')).map(cb => cb.value);
    const ministryDate = document.getElementById('ministryDate').value;
    
    // Get values that match the database schema
    formData.append('Nome', selectedOption.getAttribute('data-nome'));
    formData.append('CPF', selectedOption.getAttribute('data-cpf'));
    formData.append('Numero', selectedOption.getAttribute('data-numero'));
    formData.append('Email', selectedOption.getAttribute('data-email'));
    formData.append('foto_path', selectedOption.getAttribute('data-foto'));
    formData.append('nrs', JSON.stringify(selectedNRs));
    formData.append('ministryDate', ministryDate);
    
    // Disable the generate button while processing
    const generateButton = document.getElementById('generateButton');
    generateButton.disabled = true;
    
    fetch('/generate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessModal(data.pptx_path, data.pdf_path);
        } else {
            showErrorModal(data.error || 'Erro ao gerar certificado');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorModal('Erro ao processar a requisição');
    })
    .finally(() => {
        // Re-enable the generate button after processing
        generateButton.disabled = false;
        updateGenerateButton();
    });
}

// Adiciona o event listener ao formulário
document.getElementById('certificateForm').addEventListener('submit', handleFormSubmit);

// Função para habilitar/desabilitar o botão de gerar certificado
function updateGenerateButton() {
    const collaborator = document.getElementById('collaborator').value;
    const selectedNRs = document.querySelectorAll('input[name="nrs"]:checked');
    const generateButton = document.getElementById('generateButton');
    
    generateButton.disabled = !collaborator || selectedNRs.length === 0;
}

// Adiciona listeners para atualizar o estado do botão
document.getElementById('collaborator').addEventListener('change', updateGenerateButton);
document.querySelectorAll('input[name="nrs"]').forEach(checkbox => {
    checkbox.addEventListener('change', updateGenerateButton);
});

// Inicializa o estado do botão
updateGenerateButton();

// Funções para gerenciamento de funcionários
async function adicionarFuncionario(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch('/gerenciar/adicionar', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Recarrega a página após sucesso
            window.location.reload();
        } else {
            showErrorModal(data.error || 'Erro ao adicionar funcionário.');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorModal('Erro ao processar a requisição. Por favor, tente novamente.');
    }
}

async function atualizarFuncionario(event, id) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch(`/gerenciar/atualizar/${id}`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            window.location.reload();
        } else {
            showErrorModal(data.error || 'Erro ao atualizar funcionário.');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorModal('Erro ao processar a requisição. Por favor, tente novamente.');
    }
}

async function excluirFuncionario(id) {
    if (!confirm('Tem certeza que deseja excluir este funcionário?')) {
        return;
    }

    try {
        const response = await fetch(`/gerenciar/excluir/${id}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            window.location.reload();
        } else {
            showErrorModal(data.error || 'Erro ao excluir funcionário.');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorModal('Erro ao processar a requisição. Por favor, tente novamente.');
    }
}

async function carregarDetalhesFuncionario(id) {
    try {
        const response = await fetch(`/gerenciar/funcionario/${id}`);
        const data = await response.json();

        if (response.ok && data.success) {
            // Preenche o formulário de edição com os dados do funcionário
            document.getElementById('edit-nome').value = data.funcionario.nome;
            document.getElementById('edit-cpf').value = data.funcionario.cpf;
            document.getElementById('edit-numero').value = data.funcionario.numero;
            document.getElementById('edit-email').value = data.funcionario.email;
            
            // Atualiza a preview da foto atual
            const fotoPreview = document.getElementById('edit-foto-preview');
            if (fotoPreview) {
                fotoPreview.src = data.funcionario.foto_url;
                fotoPreview.style.display = 'block';
            }

            // Abre o modal de edição
            const editModal = new bootstrap.Modal(document.getElementById('editFuncionarioModal'));
            editModal.show();
        } else {
            showErrorModal(data.error || 'Erro ao carregar detalhes do funcionário.');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorModal('Erro ao carregar detalhes do funcionário.');
    }
}

// Funções para gerenciamento de fotos
function previewImagem(input, previewId) {
    const preview = document.getElementById(previewId);
    const placeholder = document.getElementById(previewId + 'Placeholder');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.classList.remove('d-none');
            if (placeholder) {
                placeholder.classList.add('d-none');
            }
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Função para gerenciar foto
function gerenciarFoto(id) {
    const modal = new bootstrap.Modal(document.getElementById('gerenciarFotoModal'));
    const fotoPreview = document.getElementById('gerenciarFotoPreview');
    const fotoPlaceholder = document.getElementById('gerenciarFotoPlaceholder');
    const btnExcluirFoto = document.getElementById('btnExcluirFoto');
    
    // Configurar o ID do colaborador no formulário
    document.getElementById('gerenciarFotoId').value = id;
    
    // Obter o caminho da foto atual
    const select = document.getElementById('collaborator');
    const option = select.options[select.selectedIndex];
    const fotoPath = option.getAttribute('data-foto');
    
    // Atualizar preview no modal
    if (fotoPath) {
        fotoPreview.src = '/' + fotoPath;
        fotoPreview.classList.remove('d-none');
        fotoPlaceholder.classList.add('d-none');
        btnExcluirFoto.disabled = false;
    } else {
        fotoPreview.classList.add('d-none');
        fotoPlaceholder.classList.remove('d-none');
        btnExcluirFoto.disabled = true;
    }
    
    modal.show();
}

// Função para atualizar foto
async function atualizarFoto() {
    const id = document.getElementById('gerenciarFotoId').value;
    const input = document.getElementById('gerenciarFotoInput');
    
    if (!input.files || !input.files[0]) {
        showErrorModal('Por favor, selecione uma foto para upload');
        return;
    }
    
    const formData = new FormData();
    formData.append('foto', input.files[0]);
    
    try {
        const response = await fetch(`/gerenciar/atualizar_foto/${id}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            location.reload();
        } else {
            showErrorModal(data.error || 'Erro ao atualizar foto');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorModal('Erro ao processar a requisição');
    }
}

// Função para excluir foto
async function excluirFoto() {
    if (!confirm('Tem certeza que deseja excluir a foto?')) {
        return;
    }
    
    const id = document.getElementById('gerenciarFotoId').value;
    
    try {
        const response = await fetch(`/gerenciar/excluir_foto/${id}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            location.reload();
        } else {
            showErrorModal(data.error || 'Erro ao excluir foto');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorModal('Erro ao processar a requisição');
    }
}

// Função para atualizar a foto do colaborador quando selecionado
function atualizarFotoColaborador() {
    const select = document.getElementById('collaborator');
    const option = select.options[select.selectedIndex];
    const fotoPath = option ? option.getAttribute('data-foto') : '';
    
    const preview = document.getElementById('fotoPreview');
    const placeholder = document.getElementById('fotoPlaceholder');
    
    if (fotoPath) {
        preview.src = '/' + fotoPath;
        preview.classList.remove('d-none');
        placeholder.classList.add('d-none');
    } else {
        preview.classList.add('d-none');
        placeholder.classList.remove('d-none');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Listener para mudança de colaborador
    const collaboratorSelect = document.getElementById('collaborator');
    if (collaboratorSelect) {
        collaboratorSelect.addEventListener('change', function() {
            atualizarFotoColaborador();
            updateGenerateButton();
        });
    }

    // Adicionar click handler para o container da foto
    const fotoContainer = document.getElementById('fotoContainer');
    if (fotoContainer) {
        fotoContainer.addEventListener('click', function() {
            const select = document.getElementById('collaborator');
            if (!select.value) {
                showErrorModal('Por favor, selecione um colaborador primeiro');
                return;
            }
            gerenciarFoto(select.value);
        });
    }

    // Preview da foto no modal
    const gerenciarFotoInput = document.getElementById('gerenciarFotoInput');
    if (gerenciarFotoInput) {
        gerenciarFotoInput.addEventListener('change', function() {
            const preview = document.getElementById('gerenciarFotoPreview');
            const placeholder = document.getElementById('gerenciarFotoPlaceholder');
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.classList.remove('d-none');
                    placeholder.classList.add('d-none');
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Inicializa o estado do botão e a foto
    updateGenerateButton();
    atualizarFotoColaborador();
}); 