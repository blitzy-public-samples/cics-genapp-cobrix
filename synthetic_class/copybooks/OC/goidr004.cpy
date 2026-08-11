******************************************************************
*  COPYBOOK  : GOIDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : ID
******************************************************************
 01  RT-OID-RATING.

          03 RT-OID-TERRITORY-CODE            PIC X(3).
          03 RT-OID-CLASS-CODE                PIC X(4).
          03 RT-OID-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OID-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OID-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OID-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OID-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OID-RATED-PREMIUM             PIC 9(9)V9(2).
