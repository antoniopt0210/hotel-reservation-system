const Input = ({
  id,
  label,
  type = 'text',
  value,
  onChange,
  placeholder = '',
  required = false,
  className = '',
  error = '',
}) => (
  <div className={`flex flex-col gap-1 ${className}`}>
    {label && (
      <label htmlFor={id} className="text-sm font-medium text-gray-700">
        {label}
      </label>
    )}
    <input
      id={id}
      name={id}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      required={required}
      className={`
        w-full px-4 py-2 border rounded-md text-gray-800
        focus:outline-none focus:ring-2 focus:ring-blue-400
        ${error ? 'border-red-500' : 'border-gray-300'}
      `}
    />
    {error && <p className="text-xs text-red-500">{error}</p>}
  </div>
);

export default Input;
