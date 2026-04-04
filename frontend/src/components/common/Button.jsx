const VARIANTS = {
  primary:   'bg-blue-600 text-white hover:bg-blue-700',
  secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
  success:   'bg-green-500 text-white hover:bg-green-600',
  warning:   'bg-yellow-500 text-white hover:bg-yellow-600',
  danger:    'bg-red-500 text-white hover:bg-red-600',
};

const SIZES = {
  sm: 'py-1 px-3 text-sm',
  md: 'py-2 px-4 text-sm',
  lg: 'py-2 px-6 text-base',
};

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  type = 'button',
  onClick,
}) => (
  <button
    type={type}
    onClick={onClick}
    disabled={disabled}
    className={`
      inline-flex items-center justify-center rounded-md font-medium
      transition duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1
      disabled:opacity-50 disabled:cursor-not-allowed
      ${VARIANTS[variant]} ${SIZES[size]} ${className}
    `}
  >
    {children}
  </button>
);

export default Button;
