import { Navbar, Container, Nav, Button } from "react-bootstrap";
import { Link } from "react-router-dom";

const BaseLayout = ({ children }) => {
  return (
    <>
      <Navbar expand="lg" className="navbar">
        <Container fluid>
          <Navbar.Brand as={Link} to="/">
            <img
              src="/assets/VEC-banner.png"
              alt="LOGO"
              width="380"
              height="100"
              className="navbar-logo"
            />
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="navbarNav" />
          <Navbar.Collapse id="navbarNav" className="navbar-collapse-custom">
            <Nav>
              <Nav.Item>
                <Button
                  as={Link}
                  to="/signup"
                  variant="custom-orange"
                  className="nav-button"
                >
                  Student Signup
                </Button>
              </Nav.Item>
              <Nav.Item>
                <Button
                  as={Link}
                  to="/events"
                  variant="custom-orange"
                  className="nav-button"
                >
                  Literacy Club Events
                </Button>
              </Nav.Item>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      {children}
    </>
  );
};

export default BaseLayout;
