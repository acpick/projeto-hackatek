function deleteItem(itemId)
{
    fetch('/delete-item', {method: 'POST', body: JSON.stringify({itemId: itemId})}).then((_res) => 
    {
        window.location.href = "/publicar";
    }
    );
}

function doarItem(itemId,quantidade)
{
    qtdDoado = document.getElementById(itemId).value

    if(quantidade < qtdDoado) {
        alert('Valor doado maior do que precisamos')
    }
    else {
        fetch('/doar-item', {method: 'POST', body: JSON.stringify({itemId: itemId,qtd:qtdDoado})}).then((_res) => 
        {
            window.location.href = "/todos_pedidos";
        }
        );
    }
}