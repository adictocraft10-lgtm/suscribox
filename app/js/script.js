document.addEventListener('DOMContentLoaded', () => {
    const stage = new Konva.Stage({
        container: 'editor',
        width: document.querySelector('.editor-stage').clientWidth,
        height: document.querySelector('.editor-stage').clientHeight,
    });

    const layer = new Konva.Layer();
    stage.add(layer);

    let frameImage;
    const userImage = new Konva.Image({
        draggable: true,
    });
    layer.add(userImage);

    // Cargar marcos
    const marcosGallery = document.getElementById('marcos-gallery');
    fetch('/marcos')
        .then(response => response.json())
        .then(files => {
            files.forEach(file => {
                const img = document.createElement('img');
                img.src = `/marcos/${file}`;
                img.addEventListener('click', () => {
                    Konva.Image.fromURL(img.src, (imgNode) => {
                        if (frameImage) frameImage.destroy();
                        frameImage = imgNode;
                        frameImage.setAttrs({
                            x: 0,
                            y: 0,
                            width: stage.width(),
                            height: stage.height(),
                        });
                        layer.add(frameImage);
                        userImage.moveToTop();
                        layer.draw();
                    });
                });
                marcosGallery.appendChild(img);
            });
        });

    // Cargar stickers
    const stickersGallery = document.getElementById('stickers-gallery');
    fetch('/stickers')
        .then(response => response.json())
        .then(files => {
            files.forEach(file => {
                const img = document.createElement('img');
                img.src = `/stickers/${file}`;
                img.addEventListener('click', () => {
                    Konva.Image.fromURL(img.src, (stickerNode) => {
                        stickerNode.setAttrs({
                            x: 50,
                            y: 50,
                            width: 100,
                            height: 100,
                            draggable: true,
                        });
                        layer.add(stickerNode);
                        addTransformer(stickerNode);
                        layer.draw();
                    });
                });
                stickersGallery.appendChild(img);
            });
        });

    // Cargar imagen de usuario
    document.getElementById('image-uploader').addEventListener('change', (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (event) => {
            Konva.Image.fromURL(event.target.result, (imgNode) => {
                userImage.image(imgNode.image());
                userImage.setAttrs({
                    x: 50,
                    y: 50,
                    width: 200,
                    height: 200,
                });
                addTransformer(userImage);
                userImage.moveToTop();
                if(frameImage) frameImage.moveToBottom();
                layer.draw();
            });
        };
        reader.readAsDataURL(file);
    });

    // Añadir texto
    document.getElementById('add-text').addEventListener('click', () => {
        const textNode = new Konva.Text({
            text: 'Doble click para editar',
            x: 50,
            y: 80,
            fontSize: 20,
            draggable: true,
            fill: 'black',
        });
        layer.add(textNode);
        addTransformer(textNode);

        textNode.on('dblclick', () => {
            const textPosition = textNode.getAbsolutePosition();
            const stageBox = stage.container().getBoundingClientRect();

            const areaPosition = {
                x: stageBox.left + textPosition.x,
                y: stageBox.top + textPosition.y,
            };

            const textarea = document.createElement('textarea');
            document.body.appendChild(textarea);

            textarea.value = textNode.text();
            textarea.style.position = 'absolute';
            textarea.style.top = areaPosition.y + 'px';
            textarea.style.left = areaPosition.x + 'px';
            textarea.style.width = textNode.width();

            textarea.focus();

            textarea.addEventListener('keydown', (e) => {
                if (e.keyCode === 13 && !e.shiftKey) {
                    textNode.text(textarea.value);
                    document.body.removeChild(textarea);
                    layer.draw();
                } else if (e.keyCode === 27) {
                    document.body.removeChild(textarea);
                }
            });
        });
        layer.draw();
    });

    // Descargar imagen
    document.getElementById('download-btn').addEventListener('click', () => {
        // Ocultar transformadores antes de descargar
        stage.find('Transformer').forEach(tr => tr.hide());
        layer.draw();

        const dataURL = stage.toDataURL({ pixelRatio: 2 });
        const link = document.createElement('a');
        link.download = 'mi-creacion.png';
        link.href = dataURL;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Mostrar transformadores de nuevo
        stage.find('Transformer').forEach(tr => tr.show());
        layer.draw();
    });

    // Función para añadir transformador
    function addTransformer(node) {
        const tr = new Konva.Transformer();
        layer.add(tr);
        tr.nodes([node]);

        // Ocultar otros transformadores
        stage.on('click tap', (e) => {
            if (e.target === stage) {
                stage.find('Transformer').forEach(t => t.nodes([]));
                return;
            }
            if (!e.target.hasName('selectable')) {
                return;
            }
            const metaPressed = e.evt.shiftKey || e.evt.ctrlKey || e.evt.metaKey;
            const isSelected = tr.nodes().indexOf(e.target) >= 0;

            if (!metaPressed && !isSelected) {
                tr.nodes([e.target]);
            } else if (metaPressed && isSelected) {
                const nodes = tr.nodes().slice();
                nodes.splice(nodes.indexOf(e.target), 1);
                tr.nodes(nodes);
            } else if (metaPressed && !isSelected) {
                const nodes = tr.nodes().concat([e.target]);
                tr.nodes(nodes);
            }
        });
    }

    window.addEventListener('resize', () => {
        const container = document.querySelector('.editor-stage');
        stage.width(container.clientWidth);
        stage.height(container.clientHeight);
        if (frameImage) {
            frameImage.width(stage.width());
            frameImage.height(stage.height());
        }
        layer.draw();
    });
});
