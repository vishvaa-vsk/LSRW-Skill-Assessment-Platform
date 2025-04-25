import { Alert as BootstrapAlert } from "react-bootstrap";

const Alert = ({ message, variant, onClose }) => {
  if (!message) return null;

  return (
    <BootstrapAlert variant={variant} dismissible onClose={onClose}>
      {message}
    </BootstrapAlert>
  );
};

export default Alert;
