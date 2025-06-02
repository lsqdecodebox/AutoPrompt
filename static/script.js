async function optimize() {
    const example_text = document.getElementById('example_text').value;
    const expected_output = document.getElementById('expected_output').value;
    const target_text = document.getElementById('target_text').value;
    const last_prompt = document.getElementById('last_prompt').value || '无';

    if (!example_text || !expected_output) {
        alert('请填写示例文本和期望输出！');
        return;
    }

    // 设置按钮为加载状态
    const button = document.getElementById('optimize-btn');
    const spinner = button.querySelector('.spinner-border');
    const btnText = button.querySelector('.btn-text');
    
    button.disabled = true;
    spinner.classList.remove('d-none');
    btnText.textContent = '优化中...';

    try {
        const response = await fetch('/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                example_text,
                expected_output,
                target_text,
                last_prompt
            })
        });

        const result = await response.json();
        
        if (result.status === 'success') {
            // 更新最佳结果
            document.getElementById('best_template').textContent = result.data.best_template;
            document.getElementById('best_response').textContent = result.data.best_response;
            document.getElementById('result_response').textContent = result.data.result_response;
            document.getElementById('best_similarity_score').textContent = result.data.best_similarity_score.toFixed(4);
            document.getElementById('best_generality_score').textContent = result.data.best_generality_score.toFixed(4);

            // 更新结果表格
            const tbody = document.getElementById('results_table');
            tbody.innerHTML = ''; // 清空现有内容

            result.data.all_templates.forEach((template, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td><pre class="result-text">${template}</pre></td>
                    <td><pre class="result-text">${result.data.all_responses[index]}</pre></td>
                    <td>${result.data.all_similarities[index].toFixed(4)}</td>
                    <td>${result.data.all_generalities[index].toFixed(4)}</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            alert('优化失败：' + result.message);
        }
    } catch (error) {
        alert('发生错误：' + error.message);
    } finally {
        // 恢复按钮状态
        button.disabled = false;
        spinner.classList.add('d-none');
        btnText.textContent = '优化提示词';
    }
} 