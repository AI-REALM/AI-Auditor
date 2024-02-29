import re

def escape_special_characters(text):
    # Define the pattern for special characters that need to be escaped
    pattern = r'(\\|\*|`|~|#|\+|-|=|\|)'
    
    # Use the sub method from re to replace the characters with their escaped versions
    escaped_text = re.sub(pattern, r'\\\1', text)
    
    return escaped_text

# Example usage:
input_text = """<b>1. Transfer Fee</b> ❕
<i>A fee has been discovered within the contract.</i>

<code>Issues: 1</code>
<pre>Transfer Fee: OASIS.transfer(address,uint256) (OASIS.sol#231-234)
        - in nested function: _transfer
                - in expression: amount.mul(_buyTax).div(100)
                - in expression: amount.mul(_sellTax).div(100)
                - in expression: amount.mul(_transferTax).div(100)
                - in expression: 0
                - in expression: 0
                - in expression: 5
</pre><b>Transfer Fee Limits: </b>Current transfer fee upper limit is: 15%.
Lower limit not found.
<b>Current fee: </b>15%
<b>Relevant Function Snippet: </b>
<pre>function transfer(address recipient, uint256 amount) public override returns (bool) {
    _transfer(_msgSender(), recipient, amount);
    return true;
}</pre>

<b>2. Transfer Limit</b> ❕
<i>The max/min amount of token transferred can be limited (max could be set to 0).</i>

<code>Issues: 1</code>
<pre>Transfer amount limits in: OASIS.transferFrom(address,address,uint256) (OASIS.sol#245-249)
        - In expression: balanceOf(to) + amount
        - In expression: balanceOf(to) + amount <= maxWalletLimit
</pre><b>Transfer Amount Limits: </b>Maximum transfer amount: 100% of total supply (1B OASIS).
Minimum transfer amount not found.
<b>Transfer Limit Modifiable: </b>No
<b>Relevant Function Snippet: </b>
<pre>function transferFrom(address sender, address recipient, uint256 amount) public override returns (bool) {
    _transfer(sender, recipient, amount);
    _approve(sender, _msgSender(), _allowances[sender][_msgSender()].sub(amount, "ERC20: transfer amount exceeds allowance"));
    return true;
}</pre>
<code>Issues: 2</code>
<pre>Transfer amount limits in: OASIS.transfer(address,uint256) (OASIS.sol#231-234)
        - In expression: balanceOf(to) + amount
        - In expression: balanceOf(to) + amount <= maxWalletLimit
</pre><b>Transfer Amount Limits: </b>Maximum transfer amount: 100% of total supply (1B OASIS).
Minimum transfer amount not found.
<b>Transfer Limit Modifiable: </b>No
<b>Relevant Function Snippet: </b>
<pre>function transfer(address recipient, uint256 amount) public override returns (bool) {
    _transfer(_msgSender(), recipient, amount);
    return true;
}</pre>

<b>3. Recently Deployed Contract
</b> ❕
<i>The smart contract was deployed less than 14 days ago.</i>

<code>Issues: 1</code>
<pre>The smart contract was deployed less than 14 days ago. Please be careful as it could be a new contract or a fake one.</pre><b>Contract Deployment Date: </b>21-Feb-24 00:36:11 UTC


<b>4. Liquidity Drain</b> ❕
<i>Our algorithms have identified a sudden and massive withdrawal from the liquidity pool, which may impact the ability to sell the token.</i>

<code>Issues: 1</code>
<pre>Our algorithms have identified a sudden and massive withdrawal from the liquidity pool, which may impact the ability to sell the token.</pre>"""
escaped_text = escape_special_characters(input_text)
print(escaped_text)