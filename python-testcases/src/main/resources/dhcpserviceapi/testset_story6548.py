"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     January 2015
@author:    Kieran Duggan, Boyan Mihovski
@summary:   Integration
            Agile: STORY LITPCDS-6548
"""

from litp_generic_test import GenericTest, attr
from litp_cli_utils import CLIUtils


class Story6548(GenericTest):
    """
    As a LITP user I want to specify a DHCP service to run on a
    pair of peer nodes so that there is a DHCP service available
    for virtual machines running in the LITP complex (ipv4 only).
    """

    def setUp(self):
        """
        Description:
            Runs before every single test.
        Actions:
            1. Call the super class setup method.
            2. Set up variables used in the tests.
        Results:
            The super class prints out diagnostics and
            variables common to all tests are available.
        """
        # 1. Call super class setup
        super(Story6548, self).setUp()

        # 2. Set up variables used in the test
        self.cli = CLIUtils()
        self.ms_node = self.get_management_node_filenames()[0]
        self.node_urls = self.find(self.ms_node, "/deployments", "node")
        self.range_props = "start={0} end={1}"
        self.no_expected_error = "Expected '{0}' not in stderr"

    def tearDown(self):
        """
        Description:
            Run after each test.
        Actions:
            1. Cleanup after test if global results value has been used
            2. Call the superclass teardown method
        Results:
            Items used in the test are cleaned up and the
            super class prints out end test diagnostics
        """
        super(Story6548, self).tearDown()

    def _create_test_network_and_interfaces(self):
        """
        Description:
            Create one LITP test network interface per node in deployment.
        Actions:
            1. Create one test LITP network interface for one DHCP subnet.
        Results:
            litp create command for direct plan task execution.
        """
        # Add an eth to the nodes with an ipaddress on the associated network
        free_nics = self.verify_backup_free_nics(
            self.ms_node, self.node_urls[0])
        test_node_if1 = free_nics[0]

        # node1 eth
        if_url = self.node_urls[0] + "/network_interfaces/if_6548"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.1'".\
                    format(test_node_if1["MAC"], test_node_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        free_nics = self.verify_backup_free_nics(
            self.ms_node, self.node_urls[1])
        test_node2_if1 = free_nics[0]

        # node2 eth
        if_url = self.node_urls[1] + "/network_interfaces/if_6548"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.2'".\
                    format(test_node2_if1["MAC"], test_node2_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

    @attr('all', 'revert', 'story6548', 'story6548_tc19')
    def test_19_n_non_ipv4_address_dhcp_range(self):
        """
        @tms_id: litpcds_6548_tc19
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create dhcp range with non-ipv4 addresses
        @tms_description:
        1) Verify a CardinalityError is thrown when
            creating a dhcp service without a dhcp subnet
        2) Verify a CardinalityError is thrown when
            creating a dhcp service without dhcp range
        3) Verify a ValidationError is thrown when
            creating a dhcp range with non-ipv4 addresses
        @tms_test_steps:
            @step: Create dhcp-service item-type
            @result: Item is created
            @step: Execute "litp create_plan"
            @result: Error thrown: CardinalityError
            @result: Error message: This collection requires a
                minimum of 1 items not marked for removal
            @step: Create dhcp-subnet item-type
            @result: Item is created
            @step: Inherit item onto node1
            @result: Item is inherited onto node1
            @step: Execute "litp create_plan"
            @result: Error thrown: CardinalityError
            @result: Error message: This collection requires a
                minimum of 1 items not marked for removal
            @step: Create dhcp-range with invalid
                values: "alphabetical characters"
            @result: ValidationError: Invalid value,
                IPv4 Address must be specified
            @step: Create dhcp-range with invalid values: "empty spaces"
            @result:ValidationError: Invalid value,
                IPv4 Address must be specified
            @step: Create dhcp-range with invalid values: "ipv6"
            @result:ValidationError: Invalid value,
                IPv4 Address must be specified
            @step: Create dhcp-range with invalid
                values: start range higher than end range
            @result:ValidationError: Invalid value, IP address
                must be greater than or equal to "start" IP address
        @tms_test_precondition: None
        @tms_execution_type: Automated
        """
        self.log("info", "1. Create dhcp-service item-type.")
        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.log("info", "BEGINNING TEST #6 - "
                         "Create DHCP service without DHCP subnet.")

        # Expected errors
        cardinality_error = "CardinalityError"
        no_items_removal = "This collection requires a minimum " \
                           "of 1 items not marked for removal"

        self.log("info", "2. Attempt to create a plan.")
        _, std_err, _ = self.execute_cli_createplan_cmd(
            self.ms_node, expect_positive=False)

        self.log("info", "2.1. Assert that a 'CardinalityError' is "
                         "returned with correct error.")
        self.assertTrue(self.is_text_in_list(cardinality_error, std_err),
                        self.no_expected_error.format(cardinality_error))
        self.assertTrue(self.is_text_in_list(no_items_removal, std_err),
                        self.no_expected_error.format(no_items_removal))

        self.log("info", "BEGINNING TEST #7 - "
                         "Create DHCP service without DHCP range.")
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        self.log("info", "3. Create test network.")
        network_url = networks_path + "/test_network6548"
        props = "name='test1' subnet='10.10.10.0/24'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        self.log("info", "4. Create dhcp-subnet item-type.")
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.log("info", "5. Inherit dhcp-subnet item onto node1.")
        node1_dhcp_url = self.node_urls[0] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        self.log("info", "6. Attempt to create a plan.")
        _, std_err, _ = self.execute_cli_createplan_cmd(
            self.ms_node, expect_positive=False)

        self.log("info", "6.1. Assert that a 'CardinalityError' is "
                         "returned with correct error.")
        self.assertTrue(self.is_text_in_list(cardinality_error, std_err),
                        self.no_expected_error.format(cardinality_error))
        self.assertTrue(self.is_text_in_list(no_items_removal, std_err),
                        self.no_expected_error.format(no_items_removal))

        self.log("info", "7. Remove inherited dhcp-subnet item from node1.")
        self.execute_cli_remove_cmd(self.ms_node, node1_dhcp_url)

        self.log("info", "BEGINNING TEST #19 - "
                         "Create DHCP range with non-IPv4 addresses.")

        self.log("info", "8. Create one LITP test network "
                         "interface per node in the deployment.")
        self._create_test_network_and_interfaces()

        # Expected errors
        validation_error = "ValidationError"
        invalid_value = "Invalid value"
        ipv4_specified = "IPv4 Address must be specified"

        self.log("info", "9. Attempt to create dhcp-range "
                         "with alphabetical characters.")
        range_start = "abc"
        range_end = "def"
        props = self.range_props.format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        _, std_err, _ = self.execute_cli_create_cmd(self.ms_node, range_url,
                                                    "dhcp-range", props,
                                                    expect_positive=False)

        self.log("info", "9.1. Assert that a 'ValidationError' is "
                         "returned with correct error.")
        self.assertTrue(self.is_text_in_list(validation_error, std_err),
                        self.no_expected_error.format(validation_error))
        self.assertTrue(self.is_text_in_list(invalid_value, std_err),
                        self.no_expected_error.format(invalid_value))
        self.assertTrue(self.is_text_in_list(ipv4_specified, std_err),
                        self.no_expected_error.format(ipv4_specified))

        self.log("info", "10. Attempt to create dhcp-range "
                         "with empty spaces.")
        range_start = " "
        range_end = " "
        props = self.range_props.format(range_start, range_end)

        _, std_err, _ = self.execute_cli_create_cmd(self.ms_node, range_url,
                                                    "dhcp-range", props,
                                                    expect_positive=False)

        self.log("info", "10.1. Assert that a 'ValidationError' is "
                         "returned with correct error.")
        self.assertTrue(self.is_text_in_list(validation_error, std_err),
                        self.no_expected_error.format(validation_error))
        self.assertTrue(self.is_text_in_list(invalid_value, std_err),
                        self.no_expected_error.format(invalid_value))
        self.assertTrue(self.is_text_in_list(ipv4_specified, std_err),
                        self.no_expected_error.format(ipv4_specified))

        self.log("info", "11. Attempt to create dhcp-range "
                         "with IPv6 value.")
        range_start = "2001:abcd:ef::11"
        range_end = "2001:abcd:ef::15"
        props = self.range_props.format(range_start, range_end)

        _, std_err, _ = self.execute_cli_create_cmd(self.ms_node, range_url,
                                                    "dhcp-range", props,
                                                    expect_positive=False)

        self.log("info", "11.1. Assert that a 'ValidationError' is "
                         "returned with correct error.")
        self.assertTrue(self.is_text_in_list(validation_error, std_err),
                        self.no_expected_error.format(validation_error))
        self.assertTrue(self.is_text_in_list(invalid_value, std_err),
                        self.no_expected_error.format(invalid_value))
        self.assertTrue(self.is_text_in_list(ipv4_specified, std_err),
                        self.no_expected_error.format(ipv4_specified))

        self.log("info", "12. Attempt to create dhcp-range where the "
                         "start range is higher than the end range.")
        range_start = "10.10.10.7"
        range_end = "10.10.10.4"
        props = self.range_props.format(range_start, range_end)

        _, std_err, _ = self.execute_cli_create_cmd(self.ms_node, range_url,
                                                    "dhcp-range", props,
                                                    expect_positive=False)

        self.log("info", "12.1. Assert that a 'ValidationError' is "
                         "returned with correct error.")
        invalid_range = 'Invalid IP range: "end" IP address must ' \
                        'be greater than or equal to "start" IP address'
        self.assertTrue(self.is_text_in_list(validation_error, std_err),
                        self.no_expected_error.format(validation_error))
        self.assertTrue(self.is_text_in_list(invalid_range, std_err),
                        self.no_expected_error.format(invalid_range))
